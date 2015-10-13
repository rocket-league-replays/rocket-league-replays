from django import template

from ..models import Replay

register = template.Library()


@register.assignment_tag
def get_replay_by_pk(pk):
    try:
        return Replay.objects.get(pk=pk)
    except Replay.DoesNotExist:
        return None


@register.inclusion_tag('replays/includes/scoreboard.html', takes_context=True)
def scoreboard(context, team):
    return {
        'players': context['replay'].player_set.filter(
            team=team,
        ),
        'team': team,
        'team_str': 'Blue' if team == 0 else 'Orange'
    }
