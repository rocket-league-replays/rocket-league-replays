import json
import math
import subprocess
from pprint import pprint

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Replay
from ...parser import Parser


def distance(pos1, pos2):
    xd = pos2[0] - pos1[0]
    yd = pos2[1] - pos1[1]
    zd = pos2[2] - pos1[2]

    return math.sqrt(xd * xd + yd * yd + zd * zd)


class Command(BaseCommand):

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('replay', nargs='?', type=int)

    def handle(self, *args, **options):
        replay_obj = Replay.objects.get(pk=options['replay'])

        if settings.DEBUG:
            replay = json.loads(subprocess.check_output('octane-binaries/octane-*-osx {}'.format(replay_obj.file.path), shell=True).decode('utf-8'))
        else:
            replay = json.loads(subprocess.check_output('octane-binaries/octane-*-linux {}'.format(replay_obj.file.url), shell=True).decode('utf-8'))

        goals = {
            goal['frame']['Value']: {'PlayerName': goal['PlayerName']['Value'], 'PlayerTeam': goal['PlayerTeam']['Value']}
            for goal in replay['Metadata']['Goals']['Value']
        }

        last_hits = {
            0: None,
            1: None
        }

        actors = {}  # All actors
        player_actors = {}  # XXX: This will be used to make the replay.save() easier.
        actor_positions = {}  # The current position data for all actors. Do we need this?
        player_cars = {}  # Car -> Player actor ID mappings.
        ball_angularvelocity = None  # The current angular velocity of the ball.
        ball_possession = None  # The team currently in possession of the ball.
        cars_frozen = False  # Whether the cars are frozen in place (3.. 2.. 1..)
        shot_data = []  # The locations of the player and the ball when goals were scored.
        unknown_boost_data = {}  # Holding dict for boosts without player data.

        location_data = []  # Used for the location JSON.
        boost_data = {}  # Used for the boost stats.
        heatmap_data = {}
        seconds_mapping = {}  # Frame -> seconds remaining mapping.

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
                    'ball': ball_position
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

            # Handle any updates to existing actors.
            for actor_id, value in frame['Updated'].items():
                actor_id = int(actor_id)

                # Merge the new properties with the existing.
                if actors[actor_id] != value:
                    actors[actor_id] = {**actors[actor_id], **value}

                if 'Engine.Pawn:PlayerReplicationInfo' in value:
                    player_actor_id = value['Engine.Pawn:PlayerReplicationInfo']['Value'][1]
                    player_cars[player_actor_id] = actor_id

            # Handle removing any destroyed actors.
            for actor_id in frame['Destroyed']:
                del actors[actor_id]

            # Loop over actors which have changed in this frame.
            for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items():
                actor_id = int(actor_id)

                # Look for any position data.
                if 'TAGame.RBActor_TA:ReplicatedRBState' in value:
                    actor_positions[actor_id] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position']

                    data_dict = {'id': actor_id}
                    data_dict['x'], data_dict['y'], data_dict['z'] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position']
                    data_dict['pitch'], data_dict['roll'], data_dict['yaw'] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Rotation']
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
                    if value['Class'] == 'TAGame.CameraSettingsActor_TA':
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

                        player_actor_id = value[csa]['Value'][1]
                        actors[player_actor_id][cs] = value[ps]['Value']

                if 'Engine.GameReplicationInfo:ServerName' in value:
                    print(value['Engine.GameReplicationInfo:ServerName']['Value'])

                if 'ProjectX.GRI_X:ReplicatedGamePlaylist' in value:
                    print(value['ProjectX.GRI_X:ReplicatedGamePlaylist']['Value'])

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
                    team_id = actors[player_id]['Engine.PlayerReplicationInfo:Team']['Value'][1]
                    team_data = actors[team_id]
                    team = int(team_data['Name'].replace('Archetypes.Teams.Team', ''))

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

        # pprint(heatmap_data)

        pprint(actors)
