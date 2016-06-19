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
        replay = Replay.objects.get(pk=options['replay'])

        if settings.DEBUG:
            self.replay = json.loads(subprocess.check_output('octane-binaries/octane-*-osx {}'.format(replay.file.path), shell=True).decode('utf-8'))
        else:
            self.replay = json.loads(subprocess.check_output('octane-binaries/octane-*-linux {}'.format(replay.file.url), shell=True).decode('utf-8'))

        goals = {
            goal['frame']: {'PlayerName': goal['PlayerName'], 'PlayerTeam': goal['PlayerTeam']}
            for goal in self.replay['Metadata']['Goals']
        }

        last_hits = {
            0: None,
            1: None
        }

        actors = {}
        actor_positions = {}
        player_cars = {}
        ball_angularvelocity = None
        ball_possession = None
        confirmed_distances = []

        for index, frame in enumerate(self.replay['Frames']):
            ball_hit = False
            confirmed_ball_hit = False
            ball_spawned = False

            if index in goals:
                # Get the ball position.
                ball_actor_id = list(filter(lambda x: actors[x]['Class'] == 'TAGame.Ball_TA', actors))[0]
                ball_position = actor_positions[ball_actor_id]
                # print(index, 'ball position data', actor_positions[ball_actor_id])

                hit_position = last_hits[goals[index]['PlayerTeam']]
                # print(index, 'last hit was', hit_position)
                # {type: 'line', dataPoints: [{x: -501, y: 4484}, {x: -679, y: 5155}]},
                # print("\t\t\t{{type: 'line', dataPoints: [{{x: {}, y: {}}}, {{x: {}, y: {}}}]}},".format(
                #     hit_position[1],
                #     hit_position[0],
                #     ball_position[1],
                #     ball_position[0],
                # ))

                print("""{{
  x: [{0}, {3}],
  y: [{1}, {4}],
  z: [{2}, {5}],
  type: 'scatter3d'
}},""".format(*hit_position, *ball_position))
                # print(index, 'distance', distance(actor_positions[ball_actor_id], hit_position))

                # Reset the last hits.
                last_hits = {
                    0: None,
                    1: None
                }
                # print()

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

            for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items():
                actor_id = int(actor_id)

                # Look for any position data.
                if 'TAGame.RBActor_TA:ReplicatedRBState' in value:
                    actor_positions[actor_id] = value['TAGame.RBActor_TA:ReplicatedRBState']['Value']['Position']

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
