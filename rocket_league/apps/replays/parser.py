import json
import math
import os
import subprocess
import time
from collections import OrderedDict
from datetime import datetime

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from pyrope import Replay as Pyrope


def distance(pos1, pos2):
    xd = pos2[0] - pos1[0]
    yd = pos2[1] - pos1[1]
    zd = pos2[2] - pos1[2]

    return math.sqrt(xd * xd + yd * yd + zd * zd)


# Convert the Pyrope data structure to the Octane structure.
def _pyrope_to_octane(replay):
    data = {}

    simple_keys = [
        'MaxChannels', 'Team0Score', 'Team1Score', 'PlayerName', 'KeyframeDelay',
        'MaxReplaySizeMB', 'NumFrames', 'MatchType', 'MapName', 'ReplayName',
        'PrimaryPlayerTeam', 'Id', 'TeamSize', 'RecordFPS', 'Date'
    ]

    for key in simple_keys:
        data[key] = {
            'Value': replay.header.get(key, '')
        }

    integers = ['Team0Score', 'Team1Score', 'NumFrames', 'PrimaryPlayerTeam']

    for key in integers:
        if data[key]['Value'] == '':
            data[key]['Value'] = 0

    if 'PlayerStats' in replay.header:
        data['PlayerStats'] = {
            'Value': []
        }

        for player in replay.header['PlayerStats']:
            player_data = {}
            simple_keys = [
                'Goals', 'Saves', 'OnlineID', 'Shots', 'Score', 'Team', 'bBot',
                'Assists', 'Name'
            ]

            for key in simple_keys:
                player_data[key] = player[key]

            player_data['Platform'] = {
                'Value': [
                    'OnlinePlatform',
                    player['Platform']['OnlinePlatform']
                ]
            }

            data['PlayerStats']['Value'].append(player_data)

    if 'Goals' in replay.header:
        data['Goals'] = {
            'Value': []
        }

        for goal in replay.header['Goals']:
            goal_data = {}
            keys = ['frame', 'PlayerName', 'PlayerTeam']

            for key in keys:
                goal_data[key] = {
                    'Value': goal[key]
                }

            data['Goals']['Value'].append(goal_data)

    return {
        'Metadata': data
    }


def _parse_header(replay_obj, replay):
    from .models import BoostData, Goal, Map, Player, Season

    Goal.objects.filter(replay=replay_obj).delete()
    Player.objects.filter(replay=replay_obj).delete()
    BoostData.objects.filter(replay=replay_obj).delete()

    assert Goal.objects.filter(replay=replay_obj).count() == 0
    assert Player.objects.filter(replay=replay_obj).count() == 0
    assert BoostData.objects.filter(replay=replay_obj).count() == 0

    # Assign the metadata to the replay object.
    replay_obj.replay_id = replay['Metadata']['Id']['Value']
    replay_obj.team_sizes = replay['Metadata']['TeamSize']['Value']
    replay_obj.team_0_score = replay['Metadata'].get('Team0Score', {'Value': 0})['Value']
    replay_obj.team_1_score = replay['Metadata'].get('Team1Score', {'Value': 0})['Value']
    replay_obj.player_name = replay['Metadata']['PlayerName']['Value']
    replay_obj.player_team = replay['Metadata'].get('PrimaryPlayerTeam', {'Value': 0})['Value']
    replay_obj.match_type = replay['Metadata']['MatchType']['Value']
    replay_obj.keyframe_delay = replay['Metadata']['KeyframeDelay']['Value']
    replay_obj.max_channels = replay['Metadata']['MaxChannels']['Value']
    replay_obj.max_replay_size_mb = replay['Metadata']['MaxReplaySizeMB']['Value']
    replay_obj.num_frames = replay['Metadata']['NumFrames']['Value']
    replay_obj.record_fps = replay['Metadata']['RecordFPS']['Value']

    if replay['Metadata'].get('MapName'):
        map_obj, created = Map.objects.get_or_create(
            slug=replay['Metadata']['MapName']['Value'].lower(),
        )
    else:
        map_obj = None

    replay_obj.map = map_obj
    replay_obj.timestamp = timezone.make_aware(
        datetime.fromtimestamp(
            time.mktime(
                time.strptime(
                    replay['Metadata']['Date']['Value'],
                    '%Y-%m-%d:%H-%M',
                )
            )
        ),
        timezone.get_current_timezone()
    )

    get_season = Season.objects.filter(
        start_date__lte=replay_obj.timestamp,
    )

    if get_season:
        replay_obj.season = get_season[0]

    if 'ReplayName' in replay['Metadata']:
        replay_obj.title = replay['Metadata']['ReplayName']['Value']

    return replay_obj, replay


def parse_replay_header(replay_id):
    from .models import Replay, Player, Goal

    replay_obj = Replay.objects.get(pk=replay_id)

    replay = Pyrope(replay_obj.file.read())

    replay = _pyrope_to_octane(replay)
    replay_obj, replay = _parse_header(replay_obj, replay)

    # Create the player objects.
    if 'PlayerStats' in replay['Metadata']:
        for player in replay['Metadata']['PlayerStats']['Value']:
            Player.objects.get_or_create(
                replay=replay_obj,
                player_name=player['Name'],
                platform=player['Platform'],
                saves=player['Saves'],
                score=player['Score'],
                goals=player['Goals'],
                shots=player['Shots'],
                team=player['Team'],
                assists=player['Assists'],
                bot=player['bBot'],
                online_id=player['OnlineID'],
            )
    else:
        # The best we can do is to get the goal scorers and the player.
        for goal in replay['Metadata'].get('Goals', {'Value': []})['Value']:
            Player.objects.get_or_create(
                replay=replay_obj,
                player_name=goal['PlayerName']['Value'],
                team=goal['PlayerTeam']['Value'],
            )

        if 'PlayerName' in replay['Metadata']:
            team = 0

            if 'PrimaryPlayerTeam' in replay['Metadata']:
                team = replay['Metadata']['PrimaryPlayerTeam']['Value']

            Player.objects.get_or_create(
                replay=replay_obj,
                player_name=replay['Metadata']['PlayerName']['Value'],
                team=team,
            )

    # Create the goal objects.
    if 'Goals' in replay['Metadata']:
        for index, goal in enumerate(replay['Metadata']['Goals']['Value']):
            player = None

            players = Player.objects.filter(
                replay=replay_obj,
                player_name=goal['PlayerName']['Value'],
                team=goal['PlayerTeam']['Value']
            )

            if players.count() > 0:
                player = players[0]
            else:
                player = Player.objects.create(
                    replay=replay_obj,
                    player_name=goal['PlayerName']['Value'],
                    team=goal['PlayerTeam']['Value']
                )

            try:
                goal_obj = Goal.objects.get(
                    replay=replay_obj,
                    frame=goal['frame']['Value'],
                    number=index + 1,
                    player=player,
                )

                goal_obj.delete()
            except Goal.DoesNotExist:
                pass

            Goal.objects.create(
                replay=replay_obj,
                frame=goal['frame']['Value'],
                number=index + 1,
                player=player,
            )

    replay_obj.processed = True
    replay_obj.crashed_heatmap_parser = False
    replay_obj.save()


def parse_replay_netstream(replay_id):
    from .models import PLATFORMS, BoostData, Goal, Player, Replay

    replay_obj = Replay.objects.get(pk=replay_id)

    try:
        if settings.DEBUG:
            if not os.path.isfile(replay_obj.file.path):
                # Download the file.
                command = 'wget https://media.rocketleaguereplays.com/{} -qO {}'.format(
                    replay_obj.file.name,
                    replay_obj.file.path,
                )

                os.system(command)

            replay = json.loads(subprocess.check_output('octane-binaries/octane-*-osx {}'.format(replay_obj.file.path), shell=True).decode('utf-8'))
        else:
            replay = json.loads(subprocess.check_output('octane-binaries/octane-*-linux {}'.format(replay_obj.file.url), shell=True).decode('utf-8'))
    except subprocess.CalledProcessError:
        # Parsing the file failed.
        replay_obj.processed = False
        replay_obj.save()
        return

    replay_obj, replay = _parse_header(replay_obj, replay)

    goals = {
        goal['frame']['Value']: {'PlayerName': goal['PlayerName']['Value'], 'PlayerTeam': goal['PlayerTeam']['Value']}
        for goal in replay['Metadata'].get('Goals', {'Value': []})['Value']
    }

    last_hits = {
        0: None,
        1: None
    }

    actors = {}  # All actors
    player_actors = {}  # XXX: This will be used to make the replay.save() easier.
    goal_actors = {}
    team_data = {}
    actor_positions = {}  # The current position data for all actors. Do we need this?
    player_cars = {}  # Car -> Player actor ID mappings.
    ball_angularvelocity = None  # The current angular velocity of the ball.
    ball_possession = None  # The team currently in possession of the ball.
    cars_frozen = False  # Whether the cars are frozen in place (3.. 2.. 1..)
    shot_data = []  # The locations of the player and the ball when goals were scored.
    unknown_boost_data = {}  # Holding dict for boosts without player data.

    location_data = []  # Used for the location JSON.
    boost_data = {}  # Used for the boost stats.
    boost_objects = []
    heatmap_data = {}
    seconds_mapping = {}  # Frame -> seconds remaining mapping.

    heatmap_json_filename = 'uploads/replay_json_files/{}.json'.format(replay_obj.replay_id)
    location_json_filename = 'uploads/replay_location_json_files/{}.json'.format(replay_obj.replay_id)

    for index, frame in enumerate(replay['Frames']):
        # Add an empty location list for this frame.
        location_data.append([])

        ball_hit = False
        confirmed_ball_hit = False
        ball_spawned = False

        if index in goals:
            # Get the ball position.
            ball_actor_id = list(filter(lambda x: actors[x]['Class'] == 'TAGame.Ball_TA', actors))[0]
            ball_position = actor_positions[ball_actor_id]

            # XXX: Update this to also register the hitter?
            hit_position = last_hits[goals[index]['PlayerTeam']]

            shot_data.append({
                'player': hit_position,
                'ball': ball_position,
                'frame': index
            })

            # Reset the last hits.
            last_hits = {
                0: None,
                1: None
            }

        # Handle any new actors.
        for actor_id, value in frame['Spawned'].items():
            actor_id = int(actor_id)

            if actor_id not in actors:
                actors[actor_id] = value

            if 'Engine.Pawn:PlayerReplicationInfo' in value:
                player_actor_id = value['Engine.Pawn:PlayerReplicationInfo']['Value'][1]
                player_cars[player_actor_id] = actor_id

            if value['Class'] == 'TAGame.Ball_TA':
                ball_spawned = True

            if value['Class'] == 'TAGame.PRI_TA':
                player_actors[actor_id] = value
                player_actors[actor_id]['joined'] = index

            if value['Class'] == 'TAGame.Team_Soccar_TA':
                team_data[actor_id] = value['Name'].replace('Archetypes.Teams.Team', '')

        # Handle any updates to existing actors.
        for actor_id, value in frame['Updated'].items():
            actor_id = int(actor_id)

            if 'Engine.PlayerReplicationInfo:Team' in value and not value['Engine.PlayerReplicationInfo:Team']['Value'][0]:
                del value['Engine.PlayerReplicationInfo:Team']

            # Merge the new properties with the existing.
            if actors[actor_id] != value:
                actors[actor_id] = {**actors[actor_id], **value}

                if actor_id in player_actors:
                    player_actors[actor_id] = actors[actor_id]

            if 'Engine.Pawn:PlayerReplicationInfo' in value:
                player_actor_id = value['Engine.Pawn:PlayerReplicationInfo']['Value'][1]
                player_cars[player_actor_id] = actor_id

        # Handle removing any destroyed actors.
        for actor_id in frame['Destroyed']:
            del actors[actor_id]

            if actor_id in player_actors:
                player_actors[actor_id]['left'] = index

        # Loop over actors which have changed in this frame.
        for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items():
            actor_id = int(actor_id)

            # Look for any position data.
            if 'TAGame.RBActor_TA:ReplicatedRBState' in value:
                actor_positions[actor_id] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position']

                # Get the player actor id.
                real_actor_id = actor_id

                for player_actor_id, car_actor_id in player_cars.items():
                    if actor_id == car_actor_id:
                        real_actor_id = player_actor_id
                        break

                if real_actor_id == actor_id:
                    real_actor_id = 'ball'

                data_dict = {'id': real_actor_id}
                data_dict['x'], data_dict['y'], data_dict['z'] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position']
                data_dict['yaw'], data_dict['pitch'], data_dict['roll'] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Rotation']
                location_data[index].append(data_dict)

            # If this property exists, the ball has changed possession.
            if 'TAGame.Ball_TA:HitTeamNum' in value:
                ball_hit = confirmed_ball_hit = True
                hit_team_num = value['TAGame.Ball_TA:HitTeamNum']['Value']
                ball_possession = hit_team_num

                # Clean up the actor positions.
                actor_positions_copy = actor_positions.copy()
                for actor_position in actor_positions_copy:
                    found = False

                    for car in player_cars:
                        if actor_position == player_cars[car]:
                            found = True

                    if not found and actor_position != ball_actor_id:
                        del actor_positions[actor_position]

            # Store the boost data for each actor at each frame where it changes.
            if 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount' in value:
                boost_value = value['TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount']['Value']
                assert 0 <= boost_value <= 255, 'Boost value {} is not in range 0-255.'.format(boost_value)

                if actor_id not in boost_data:
                    boost_data[actor_id] = {}

                # Sometimes we have a boost component without a reference to
                # a car. We don't want to lose that data, so stick it into a
                # holding dictionary until we can figure out who it belongs to.

                if 'TAGame.CarComponent_TA:Vehicle' not in actors[actor_id]:
                    if actor_id not in unknown_boost_data:
                        unknown_boost_data[actor_id] = {}

                    unknown_boost_data[actor_id][index] = boost_value
                else:
                    car_id = actors[actor_id]['TAGame.CarComponent_TA:Vehicle']['Value'][1]

                    # Find out which player this car belongs to.
                    try:
                        player_actor_id = [
                            player_actor_id
                            for player_actor_id, car_actor_id in player_cars.items()
                            if car_actor_id == car_id
                        ][0]

                        if player_actor_id not in boost_data:
                            boost_data[player_actor_id] = {}

                        boost_data[player_actor_id][index] = boost_value

                        # Attach any floating data (if we can).
                        if actor_id in unknown_boost_data:
                            for frame_index, boost_value in unknown_boost_data[actor_id].items():
                                boost_data[player_actor_id][frame_index] = boost_value

                            del unknown_boost_data[actor_id]

                    except IndexError:
                        pass

            # Store the mapping of frame -> clock time.
            if 'TAGame.GameEvent_Soccar_TA:SecondsRemaining' in value:
                seconds_mapping[index] = value['TAGame.GameEvent_Soccar_TA:SecondsRemaining']['Value']

            # See if the cars are frozen in place.
            if 'TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining' in value:
                if value['TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining']['Value'] == 3:
                    cars_frozen = True
                elif value['TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining']['Value'] == 0:
                    cars_frozen = False

            # Get the camera details.
            if 'TAGame.CameraSettingsActor_TA:ProfileSettings' in value:
                if actors[actor_id]['Class'] == 'TAGame.CameraSettingsActor_TA':
                    # Define some short variable names to stop the next line
                    # being over 200 characters long.  This block of code
                    # makes new replays have a camera structure which is
                    # similar to that of the old replays - where the camera
                    # settings are directly attached to the player rather
                    # than a CameraActor (which is what the actor in this
                    # current loop is).

                    csa = 'TAGame.CameraSettingsActor_TA:PRI'
                    ps = 'TAGame.CameraSettingsActor_TA:ProfileSettings'
                    cs = 'TAGame.PRI_TA:CameraSettings'

                    if csa in value:
                        player_actor_id = value[csa]['Value'][1]
                        actors[player_actor_id][cs] = value[ps]['Value']

            if 'Engine.GameReplicationInfo:ServerName' in value:
                replay_obj.server_name = value['Engine.GameReplicationInfo:ServerName']['Value']

            if 'ProjectX.GRI_X:ReplicatedGamePlaylist' in value:
                replay_obj.playlist = value['ProjectX.GRI_X:ReplicatedGamePlaylist']['Value']

            if 'TAGame.GameEvent_Team_TA:MaxTeamSize' in value:
                replay_obj.team_sizes = value['TAGame.GameEvent_Team_TA:MaxTeamSize']['Value']

            if 'TAGame.PRI_TA:MatchGoals' in value:
                # Get the closest goal to this frame.
                goal_actors[index] = actor_id

            if 'Engine.TeamInfo:Score' in value:
                if index not in goal_actors:
                    goal_actors[index] = actor_id

        # Work out which direction the ball is travelling and if it has
        # changed direction or speed.
        ball = None
        ball_actor_id = None
        for actor_id, value in actors.items():
            if value['Class'] == 'TAGame.Ball_TA':
                ball_actor_id = actor_id
                ball = value
                break

        ball_hit = False

        # Take a look at the ball this frame, has anything changed?
        if ball and 'TAGame.RBActor_TA:ReplicatedRBState' in ball:
            new_ball_angularvelocity = ball['TAGame.RBActor_TA:ReplicatedRBState']['Value']['AngularVelocity']

            # The ball has *changed direction*, but not necessarily been hit (it
            # may have bounced).

            if ball_angularvelocity != new_ball_angularvelocity:
                ball_hit = True

            ball_angularvelocity = new_ball_angularvelocity

            # Calculate the current distances between cars and the ball.
            # Do we have position data for the ball?
            if ball_hit and not ball_spawned and ball_actor_id in actor_positions:

                # Iterate over the cars to get the players.
                lowest_distance = None
                lowest_distance_car_actor = None

                for player_id, car_actor_id in player_cars.items():
                    # Get the team.
                    if player_id in actors and actors[player_id]['Engine.PlayerReplicationInfo:Team']['Value'][0]:
                        team_id = actors[player_id]['Engine.PlayerReplicationInfo:Team']['Value'][1]
                        team_actor = actors[team_id]
                        team = int(team_actor['Name'].replace('Archetypes.Teams.Team', ''))
                    else:
                        team = -1

                    # Make sure this actor is in on the team which is currently
                    # in possession.

                    if team != ball_possession:
                        continue

                    if car_actor_id in actor_positions:
                        actor_distance = distance(actor_positions[car_actor_id], actor_positions[ball_actor_id])

                        if not confirmed_ball_hit:
                            if actor_distance > 350:  # Value taken from the max confirmed distance.
                                continue

                        # Get the player on this team with the lowest distance.
                        if lowest_distance is None or actor_distance < lowest_distance:
                            lowest_distance = actor_distance
                            lowest_distance_car_actor = car_actor_id

                if lowest_distance_car_actor:
                    last_hits[ball_possession] = actor_positions[lowest_distance_car_actor]

        # Generate the heatmap data for this frame.  Get all of the players
        # and the ball.
        if not cars_frozen:
            moveable_actors = [
                (actor_id, value)
                for actor_id, value in actors.items()
                if value['Class'] in ['TAGame.Ball_TA', 'TAGame.PRI_TA', 'TAGame.Car_TA'] and
                (
                    'TAGame.RBActor_TA:ReplicatedRBState' in value or
                    'Position' in value
                )
            ]

            for actor_id, value in moveable_actors:
                if value['Class'] == 'TAGame.Ball_TA':
                    actor_id = 'ball'
                elif value['Class'] == 'TAGame.Car_TA':
                    if 'Engine.Pawn:PlayerReplicationInfo' not in value:
                        continue

                    actor_id = value['Engine.Pawn:PlayerReplicationInfo']['Value'][1]

                if 'TAGame.RBActor_TA:ReplicatedRBState' in value:
                    key = '{},{}'.format(
                        value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position'][0],
                        value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position'][1],
                    )
                elif 'Position' in value:
                    key = '{},{}'.format(
                        value['Position'][0],
                        value['Position'][1],
                    )

                if actor_id not in heatmap_data:
                    heatmap_data[actor_id] = {}

                if key in heatmap_data[actor_id]:
                    heatmap_data[actor_id][key] += 1
                else:
                    heatmap_data[actor_id][key] = 1

    def get_team(actor_id):
        return int(actors[actor_id]['Name'].replace('Archetypes.Teams.Team', ''))

    player_objects = {}

    # Make a dict of all the player actors and then do a bulk_create?
    for actor_id, value in player_actors.items():
        if 'Engine.PlayerReplicationInfo:UniqueId' in value:
            system = value['Engine.PlayerReplicationInfo:UniqueId']['Value']['System']
            unique_id = '{system}-{remote}-{local}'.format(
                system=value['Engine.PlayerReplicationInfo:UniqueId']['Value']['System'],
                remote=value['Engine.PlayerReplicationInfo:UniqueId']['Value']['Remote']['Value'],
                local=value['Engine.PlayerReplicationInfo:UniqueId']['Value']['Local'],
            )
            online_id = value['Engine.PlayerReplicationInfo:UniqueId']['Value']['Remote']['Value']

            if system == 'PlayStation' and 'Name' in online_id:
                online_id = online_id['Name']
        else:
            system = 'Unknown'
            unique_id = ''
            online_id = ''

        team = -1

        if 'Engine.PlayerReplicationInfo:Team' in value and value['Engine.PlayerReplicationInfo:Team']['Value'][0]:
            team = get_team(value['Engine.PlayerReplicationInfo:Team']['Value'][1])

        player_objects[actor_id] = Player.objects.create(
            replay=replay_obj,
            player_name=value['Engine.PlayerReplicationInfo:PlayerName']['Value'],
            team=team,
            score=value.get('TAGame.PRI_TA:MatchScore', {'Value': 0})['Value'],
            goals=value.get('TAGame.PRI_TA:MatchGoals', {'Value': 0})['Value'],
            shots=value.get('TAGame.PRI_TA:MatchShots', {'Value': 0})['Value'],
            assists=value.get('TAGame.PRI_TA:MatchAssists', {'Value': 0})['Value'],
            saves=value.get('TAGame.PRI_TA:MatchSaves', {'Value': 0})['Value'],
            platform=PLATFORMS.get(system, system),
            online_id=online_id,
            bot=False,  # TODO: Add a check for this.
            spectator='Engine.PlayerReplicationInfo:Team' not in value,
            actor_id=actor_id,
            unique_id=unique_id,
            camera_settings=value.get('TAGame.PRI_TA:CameraSettings', None),
            vehicle_loadout=value.get('TAGame.PRI_TA:ClientLoadout', {'Value': {}})['Value'],
            total_xp=value.get('TAGame.PRI_TA:TotalXP', {'Value': 0})['Value'],
        )

        # Store the boost data for this player.
        for boost_frame, boost_value in boost_data.get(actor_id, {}).items():
            boost_objects.append(BoostData(
                replay=replay_obj,
                player=player_objects[actor_id],
                frame=boost_frame,
                value=boost_value,
            ))

    BoostData.objects.bulk_create(boost_objects)

    # Create the goals.
    goal_objects = []
    goal_actors = OrderedDict(sorted(goal_actors.items()))

    for index, actor_id in goal_actors.items():
        # Use the player_objects dict rather than the full actors dict as
        # players who leave the game get removed from the latter.

        if actor_id in player_actors:
            goal_objects.append(Goal(
                replay=replay_obj,
                number=len(goal_objects) + 1,
                player=player_objects[actor_id],
                frame=index,
            ))

        # This actor is most likely the team object, meaning the goal was an
        # own goal scored without any of the players on the benefiting team
        # hitting the ball.

        elif actor_id in actors:
            if actors[actor_id]['Class'] == 'TAGame.Team_Soccar_TA':
                own_goal_player, created = Player.objects.get_or_create(
                    replay=replay_obj,
                    player_name='Unknown player (own goal?)',
                    team=get_team(actor_id),
                )

                goal_objects.append(Goal(
                    replay=replay_obj,
                    number=len(goal_objects) + 1,
                    player=own_goal_player,
                    frame=index,
                ))

    Goal.objects.bulk_create(goal_objects)

    # Generate heatmap and location JSON files.

    # Put together the heatmap file.
    replay_obj.heatmap_json_file = default_storage.save(
        heatmap_json_filename,
        ContentFile(json.dumps(heatmap_data, separators=(',', ':')))
    )

    # Put together the location JSON file.

    # Get rid of any boost data keys which have an empty value.
    for actor_id, data in boost_data.copy().items():
        if not data:
            del boost_data[actor_id]

    goal_data = [
        {
            'PlayerName': goal['PlayerName']['Value'],
            'PlayerTeam': goal['PlayerTeam']['Value'],
            'frame': goal['frame']['Value'],
        }
        for goal in replay['Metadata'].get('Goals', {'Value': []})['Value']
    ]

    # Trim down the actors to just the information we care about.
    player_data = {
        actor_id: {
            'type': 'player',
            'join': data['joined'],
            'left': data.get('left', replay['Metadata']['NumFrames']['Value']),
            'team': data['Engine.PlayerReplicationInfo:Team']['Value'][1],
            'name': data['Engine.PlayerReplicationInfo:PlayerName']['Value']
        }
        for actor_id, data in player_actors.items()
        if 'Engine.PlayerReplicationInfo:Team' in data
    }

    final_data = {
        'frame_data': location_data,
        'goals': goal_data,
        'boost': boost_data,
        'seconds_mapping': seconds_mapping,
        'actors': player_data,
        'teams': team_data,
    }

    replay_obj.location_json_file = default_storage.save(
        location_json_filename,
        ContentFile(json.dumps(final_data, separators=(',', ':')))
    )

    replay_obj.shot_data = shot_data
    replay_obj.processed = True
    replay_obj.show_leaderboard = True
    replay_obj.crashed_heatmap_parser = False

    replay_obj.excitement_factor = replay_obj.calculate_excitement_factor()
    replay_obj.average_rating = replay_obj.calculate_average_rating()

    replay_obj.save()
