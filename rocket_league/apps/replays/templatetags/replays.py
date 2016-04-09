import math

from django import template
from django.db.models import F, Count, Max, Sum
from django.utils.safestring import mark_safe
from collections import OrderedDict

from ..models import Goal, Player, Replay, get_default_season

register = template.Library()


@register.assignment_tag
def get_replay_by_pk(pk):
    try:
        return Replay.objects.get(pk=pk)
    except Replay.DoesNotExist:
        return None


@register.assignment_tag(takes_context=True)
def team_players(context, team):
    return {
        'players': context['replay'].player_set.filter(
            team=team,
        ),
        'team': team,
        'team_str': 'Blue' if team == 0 else 'Orange'
    }


@register.inclusion_tag('replays/includes/scoreboard.html', takes_context=True)
def scoreboard(context, team):
    return team_players(context, team)


@register.inclusion_tag('replays/includes/scoreboard.html', takes_context=True)
def custom_scoreboard(context, steam_info):
    data_dicts = []
    season_id = get_default_season()

    for size in range(1, 5):
        player_data = Player.objects.filter(
            replay__team_sizes=size,
            replay__season_id=season_id,
            platform__in=['OnlinePlatform_Steam', '1'],
            online_id=steam_info['steamid'],
        ).aggregate(
            score=Sum('score'),
            goals=Sum('goals'),
            shots=Sum('shots'),
            assists=Sum('assists'),
            saves=Sum('saves'),
        )

        if not any([player_data[k] for k in player_data]):
            continue

        # Replace any 'None' values with 0.
        for key in player_data:
            if not player_data[key]:
                player_data[key] = 0

        player_data['player_name'] = '{}v{}'.format(size, size)

        data_dicts.append(player_data)

    data_dicts.append({
        'player_name': 'Totals',
        'score': sum([key['score'] for key in data_dicts]),
        'goals': sum([key['goals'] for key in data_dicts]),
        'shots': sum([key['shots'] for key in data_dicts]),
        'assists': sum([key['assists'] for key in data_dicts]),
        'saves': sum([key['saves'] for key in data_dicts]),
    })

    return {
        'players': data_dicts,
        'team_str': 'Overall stats'
    }


@register.assignment_tag
def steam_stats(uid):
    data = {}
    season_id = get_default_season()

    # Winning goals scored.
    data['winning_goals'] = Goal.objects.filter(
        player__platform__in=['OnlinePlatform_Steam', '1'],
        player__online_id=uid,
        replay__show_leaderboard=True,
        replay__season_id=season_id,
        number=F('replay__team_0_score') + F('replay__team_1_score')
    ).count()

    # Last minute goals (literally, goals scored within the last minute of the game)
    data['last_minute_goals'] = Goal.objects.filter(
        player__platform__in=['OnlinePlatform_Steam', '1'],
        player__online_id=uid,
        replay__show_leaderboard=True,
        replay__season_id=season_id,
        frame__gte=F('replay__num_frames') - (60 * F('replay__record_fps'))
    ).count()

    # Number of times the player has scored a goal which equalised the game and
    # forced it into overtime.
    data['overtime_triggering_goals'] = 0
    data['overtime_triggering_and_winning_goals'] = 0
    data['overtime_trigger_and_team_win'] = 0

    # Find replays which went into overtime.
    replays = Replay.objects.filter(
        show_leaderboard=True,
        season_id=season_id,
        goal__frame__gte=(60 * 5 * F('record_fps')),
    )

    # Get all games with overtime goals.
    replays = Replay.objects.annotate(
        num_goals=F('team_0_score') + F('team_1_score'),
    ).filter(
        season_id=season_id,
        num_frames__gt=60 * 5 * F('record_fps'),
        show_leaderboard=True,
        player__platform__in=['OnlinePlatform_Steam', '1'],
        player__online_id=uid,
        num_goals__gte=2,
    ).prefetch_related('goal_set')

    for replay in replays:
        # Who scored the 2nd to last goal?
        try:
            goal = replay.goal_set.get(
                number=replay.num_goals - 1,
                player__platform__in=['OnlinePlatform_Steam', '1'],
                player__online_id=uid,
            )

            data['overtime_triggering_goals'] += 1

            # Did the team win?
            team = goal.player.team

            if (
                team == 0 and replay.team_0_score > replay.team_1_score or
                team == 1 and replay.team_1_score > replay.team_0_score
            ):
                data['overtime_trigger_and_team_win'] += 1

            # Did they also score the winning goal?
            replay.goal_set.get(
                number=replay.num_goals,
                player__platform__in=['OnlinePlatform_Steam', '1'],
                player__online_id=uid,
            )

            data['overtime_triggering_and_winning_goals'] += 1
        except Goal.DoesNotExist:
            pass

    # Which match size does this player appear most in?
    data['preferred_match_size'] = None

    sizes = Replay.objects.filter(
        season_id=season_id,
        show_leaderboard=True,
        player__platform__in=['OnlinePlatform_Steam', '1'],
        player__online_id=uid,
    ).values('team_sizes').annotate(
        Count('team_sizes'),
    ).order_by('-team_sizes__count')

    if len(sizes) > 0:
        data['preferred_match_size'] = sizes[0]['team_sizes']

    # What's this player's prefered role within a team?
    data['preferred_role'] = None

    role_query = Player.objects.filter(
        replay__show_leaderboard=True,
        replay__season_id=season_id,
        platform__in=['OnlinePlatform_Steam', '1'],
        online_id=uid,
    ).aggregate(
        goals=Sum('goals'),
        assists=Sum('assists'),
        saves=Sum('saves'),
    )

    if not any([v[1] for v in role_query.items()]):
        data['preferred_role'] = None
    else:
        max_stat = max(role_query, key=lambda k: role_query[k])

        if max_stat == 'goals':
            data['preferred_role'] = 'Goalscorer'
        elif max_stat == 'assists':
            data['preferred_role'] = 'Assister'
        elif max_stat == 'saves':
            data['preferred_role'] = 'Goalkeeper'

    """
    # Number of times the player's score was higher than everyone else on their
    # team put together.
    data['carries'] = 0

    # Number of times the player's score was higher than everyone else put together.
    data['dominations'] = 0

    replays = Replay.objects.filter(
        team_sizes__gte=2,
        show_leaderboard=True,
        player__platform__in=['OnlinePlatform_Steam', '1'],
        player__online_id=uid,
    )

    for replay in replays:
        # Which team was the player on? Split screen players will break a .get()
        # here, so we have to filter().
        player = replay.player_set.filter(
            platform='OnlinePlatform_Steam',
            online_id=uid,
        )[0]

        # What was the total score for this team?
        team_score = Player.objects.filter(
            replay=replay,
            team=player.team,
        ).exclude(
            pk=player.pk,
        ).aggregate(
            score=Sum('score'),
        )['score']

        if player.score > team_score:
            data['carries'] += 1

        # What was the total score for the other team?
        other_team_score = Player.objects.filter(
            replay=replay,
        ).exclude(
            team=player.team,
        ).aggregate(
            score=Sum('score'),
        )['score']

        if not team_score:
            team_score = 0

        if not other_team_score:
            other_team_score = 0

        if player.score > team_score + other_team_score:
            data['dominations'] += 1

    # The biggest gap in a win involving the player.
    data['biggest_win'] = None

    replays = Replay.objects.filter(
        team_sizes__gte=2,
        show_leaderboard=True,
        player__platform__in=['OnlinePlatform_Steam', '1'],
        player__online_id=uid,
    ).extra(select={
        'goal_diff': 'abs("team_0_score" - "team_1_score")'
    }).order_by('-goal_diff')
    """

    for replay in replays:
        # Which team was the player on? Split screen players will break a .get()
        # here, so we have to filter().
        player = replay.player_set.filter(
            platform__in=['OnlinePlatform_Steam', '1'],
            online_id=uid,
        )[0]

        # Check if the player was on the winning team.
        if (
            player.team == 0 and replay.team_0_score > replay.team_1_score or
            player.team == 1 and replay.team_1_score > replay.team_0_score
        ):
            data['biggest_win'] = mark_safe('<a href="{}">{} - {}</a>'.format(
                replay.get_absolute_url(),
                replay.team_0_score,
                replay.team_1_score,
            ))
            break

    data.update(Player.objects.filter(
        replay__season_id=season_id,
        platform__in=['OnlinePlatform_Steam', '1'],
        online_id=uid,
    ).aggregate(
        highest_score=Max('score'),
        most_goals=Max('goals'),
        most_shots=Max('shots'),
        most_assists=Max('assists'),
        most_saves=Max('saves'),
    ))

    return data


@register.assignment_tag(takes_context=True)
def user_in_replay(context):
    replay = context['replay']
    user = context['user']

    if not user.is_authenticated():
        return False

    # Is this user the uploader?
    if user == replay.user:
        return True

    # Is this user one of the players in the game?
    if user.profile.has_steam_connected():
        players = replay.player_set.filter(
            platform__in=['OnlinePlatform_Steam', '1'],
            online_id=user.social_auth.get(provider='steam').uid
        )

        if players.count() > 0:
            return True

    return False


@register.assignment_tag(takes_context=True)
def process_boost_data(context, obj=None):
    if not obj:
        obj = context['player']

    small_pickups = 0
    large_pickups = 0
    unknown_pickups = 0
    boost_consumption = 0

    data_set = obj.boostdata_set.all()

    previous_value = 85

    for data_point in data_set:
        current_value = data_point.value
        value_diff = current_value - previous_value

        if value_diff > 0:
            if current_value == 255:
                large_pickups += 1
            elif 28 <= value_diff <= 30:
                small_pickups += 1
            elif current_value == 85:  # Goal reset
                pass
            else:
                unknown_pickups += 1
        elif value_diff < 0:
            boost_consumption += math.ceil(abs(value_diff) * (100 / 255))

        previous_value = current_value

    return {
        'small_pickups': small_pickups,
        'large_pickups': large_pickups,
        'boost_consumption': boost_consumption,
        'unknown_pickups': unknown_pickups,
    }


@register.assignment_tag(takes_context=True)
def boost_chart_data(context, obj=None):
    if not obj:
        obj = context['replay']

    if not obj.eligble_for_boost_analysis():
        return {}

    players = obj.player_set.filter(spectator=False)

    goal_frames = obj.goal_set.values_list('frame', flat=True)

    boost_values = {}
    boost_consumption = {}

    team_boost_consumption = {0: {}, 1: {}}

    player_names = {}
    team_boost_values = {
        0: {},
        1: {}
    }

    boost_distribution = {0: {}, 1: {}}

    boost_consumed_values = {}
    boost_data_values = {}

    for player in players:
        actor_id = player.actor_id
        team = player.team

        if actor_id not in boost_values:
            boost_values[actor_id] = OrderedDict()

        if actor_id not in boost_consumption:
            boost_consumption[actor_id] = {}

        if actor_id not in player_names:
            player_names[actor_id] = player.player_name

        if actor_id not in boost_consumed_values:
            boost_consumed_values[actor_id] = 0

        if actor_id not in boost_data_values:
            boost_data_values[actor_id] = player.boostdata_set.all().values('frame', 'value')
            boost_data_values[actor_id] = OrderedDict((value['frame'], value['value']) for value in boost_data_values[actor_id])

        # Calculate the tween values.
        previous_value = 85
        for key, value in boost_data_values[actor_id].items():
            # If the value is 85, we need to check if a goal was just scored
            # as we don't want to tween or register boost as being consumed
            # by the goal reset.
            reset = False
            if value == 85:
                buffer_frames = set(range(key - 75, key))
                reset = len(buffer_frames.intersection(goal_frames)) > 0

            if value < previous_value:
                # Store the diff.
                # Determine how many frames of tweening this change required.
                frame_diff_required = math.floor((previous_value - value) / (255 / 74))

                if reset:
                    boost_values[actor_id][key - frame_diff_required] = math.ceil(previous_value * (100 / 255))
                else:
                    boost_consumed_values[actor_id] += math.ceil((previous_value - value) * (100 / 255))
                    boost_consumption[actor_id][key] = boost_consumed_values[actor_id]

                    if key not in team_boost_consumption[team]:
                        team_boost_consumption[team][key] = 0
                    team_boost_consumption[team][key] += math.ceil((previous_value - value) * (100 / 255))

                    for frame in range(key - frame_diff_required + 1, key):
                        tween_value = math.ceil(value + ((key - frame) * (255 / 74)))

                        if frame not in boost_values[actor_id]:
                            # Add data.
                            rendered_value = math.ceil(tween_value * (100 / 255))

                            boost_values[actor_id][frame] = rendered_value

                            if frame not in team_boost_values[team]:
                                team_boost_values[team][frame] = 0

                            team_boost_values[team][frame] += rendered_value

                            # Boost distribution
                            if rendered_value not in boost_distribution[team]:
                                boost_distribution[team][rendered_value] = 0
                            boost_distribution[team][rendered_value] += 1

                            previous_value = tween_value
            else:
                if key > 0:
                    # Add data.
                    rendered_value = math.ceil(previous_value * (100 / 255))

                    boost_values[actor_id][key - 1] = rendered_value

                    if key - 1 not in team_boost_values[team]:
                        team_boost_values[team][key - 1] = 0

                    team_boost_values[team][key - 1] += rendered_value

                    # Boost distribution
                    if rendered_value not in boost_distribution[team]:
                        boost_distribution[team][rendered_value] = 0
                    boost_distribution[team][rendered_value] += 1

            # Add data.
            rendered_value = math.ceil(value * (100 / 255))
            boost_values[actor_id][key] = rendered_value

            if key not in team_boost_values[team]:
                team_boost_values[team][key] = 0

            team_boost_values[team][key] += rendered_value

            # Boost distribution
            if rendered_value not in boost_distribution[team]:
                boost_distribution[team][rendered_value] = 0
            boost_distribution[team][rendered_value] += 1

            previous_value = value

    for key in boost_consumption:
        boost_consumption[key] = OrderedDict(sorted(boost_consumption[key].items()))

        # Ensure the last frame is present for each dict.
        if obj.num_frames not in boost_consumption[key] and len(boost_consumption[key]) > 0:
            boost_consumption[key][obj.num_frames] = boost_consumption[key][next(reversed(boost_consumption[key]))]

    team_boost_consumption_full = {0: OrderedDict(), 1: OrderedDict()}

    for key in team_boost_consumption:
        # team_boost_consumption[key] = OrderedDict(sorted(team_boost_consumption[key].items()))
        current_value = 0

        # Fix the values.
        for frame in range(obj.num_frames + 1):
            team_boost_consumption_full[key][frame] = current_value

            if frame in team_boost_consumption[key]:
                team_boost_consumption_full[key][frame] += team_boost_consumption[key][frame]

            current_value = team_boost_consumption_full[key][frame]

    for key in boost_values:
        boost_values[key] = OrderedDict(sorted(boost_values[key].items()))

        # Ensure the last frame is present for each dict.
        if obj.num_frames not in boost_values[key] and len(boost_values[key]) > 0:
            boost_values[key][obj.num_frames] = boost_values[key][next(reversed(boost_values[key]))]

    # Generate the team boost distribution charts.
    team_boost_values_full = {0: OrderedDict(), 1: OrderedDict()}

    for frame in range(obj.num_frames):
        for team in range(2):
            if frame in team_boost_values[team]:
                team_boost_values_full[team][frame] = team_boost_values[team][frame]
            else:
                if len(team_boost_values_full[team]) > 0:
                    value = team_boost_values_full[team][next(reversed(team_boost_values_full[team]))]
                else:
                    value = 0

                team_boost_values_full[team][frame] = value

    team_boost_values = team_boost_values_full

    # Get the maximum value for both teams, in terms of boost value. Pad any empty values.
    boost_distribution_full = {0: OrderedDict(), 1: OrderedDict()}
    for value in range(max(list(boost_distribution[0].keys()) + list(boost_distribution[1].keys())) + 1):
        for team in range(2):
            if value not in boost_distribution[team]:
                boost_distribution_full[team][value] = 0
            else:
                boost_distribution_full[team][value] = boost_distribution[team][value]

    return {
        'boost_values': boost_values,
        'team_boost_values': team_boost_values,
        'boost_consumption': boost_consumption,
        'team_boost_consumption': team_boost_consumption_full,
        'boost_distribution': boost_distribution_full,
        'player_names': player_names,
    }
