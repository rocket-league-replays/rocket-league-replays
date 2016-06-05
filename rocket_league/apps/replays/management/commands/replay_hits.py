from django.core.management.base import BaseCommand
import math
from pprint import pprint
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
        parser = Parser(parse_netstream=True, obj=replay)

        goals = {
            goal['frame']: {'PlayerName': goal['PlayerName'], 'PlayerTeam': goal['PlayerTeam']}
            for goal in parser.replay['meta']['properties']['Goals']
        }

        last_hits = {
            0: None,
            1: None
        }

        actors = {}
        actor_positions = {}
        player_cars = {}

        for index, frame in enumerate(parser.replay['frames']):

            if index in goals:
                print(index, 'goal data   ', goals[index])

                # Get the ball position.
                ball_actor_id = list(filter(lambda x: actors[x]['class_name'] == 'TAGame.Ball_TA', actors))[0]
                ball_position = actor_positions[ball_actor_id]
                print(index, 'ball position data', actor_positions[ball_actor_id])

                hit_position = last_hits[goals[index]['PlayerTeam']]
                print(index, 'last hit was', hit_position)
                print(index, 'distance', distance(actor_positions[ball_actor_id], hit_position))

                if goals[index]['PlayerTeam'] == 1:
                    print('Player X,Player Y,Ball X,Ball Y')
                    print(hit_position[0], ',', hit_position[1], ',', ball_position[0], ',', ball_position[1])

                # Reset the last hits.
                last_hits = {
                    0: None,
                    1: None
                }

                print('')

            for replication in frame['replications']:
                if replication['state'] == 'opening':
                    if replication['actor_id'] not in actors:
                        actors[replication['actor_id']] = replication
                elif replication['state'] == 'existing':
                    # Merge the new properties with the existing.
                    if actors[replication['actor_id']]['properties'] != replication['properties']:
                        actors[replication['actor_id']]['properties'] = {
                            **actors[replication['actor_id']]['properties'],
                            **replication['properties']
                        }

                    actors[replication['actor_id']]['state'] = 'existing'
                elif replication['state'] == 'closing':
                    del actors[replication['actor_id']]

                if replication['state'] in ['opening', 'existing']:
                    if 'Engine.Pawn:PlayerReplicationInfo' in replication['properties']:
                        player_actor_id = replication['properties']['Engine.Pawn:PlayerReplicationInfo']['contents'][1]
                        player_cars[player_actor_id] = replication['actor_id']

                # Look for any position data.
                if 'TAGame.RBActor_TA:ReplicatedRBState' in replication['properties']:
                    actor_positions[replication['actor_id']] = replication['properties']['TAGame.RBActor_TA:ReplicatedRBState']['contents'][1]

                if 'TAGame.Ball_TA:HitTeamNum' in replication['properties']:
                    hit_team_num = replication['properties']['TAGame.Ball_TA:HitTeamNum']['contents']

                    # Get the players which are on this team, then figure out
                    # where they are, then get their distance to the ball.
                    ball_actor_id = list(filter(lambda x: actors[x]['class_name'] == 'TAGame.Ball_TA', actors))[0]

                    # Find the team actor ID.
                    team_actor_id = list(filter(lambda x: actors[x]['object_name'] == 'Archetypes.Teams.Team{}'.format(hit_team_num), actors))[0]

                    # Get the players who are on this team.
                    player_actor_ids = list(filter(
                        lambda x:
                            actors[x]['object_name'] == 'TAGame.Default__PRI_TA' and
                            'Engine.PlayerReplicationInfo:Team' in actors[x]['properties'] and
                            actors[x]['properties']['Engine.PlayerReplicationInfo:Team']['contents'][1] == team_actor_id,
                        actors
                    ))

                    print(index, 'actor_positions ', actor_positions)
                    print(index, 'player_cars     ', player_cars)
                    print(index, 'HitTeamNum      ', hit_team_num)
                    print(index, 'ball_actor_id   ', ball_actor_id)
                    print(index, 'team_actor_id   ', team_actor_id)
                    print(index, 'player_actor_ids', player_actor_ids)

                    # If there is only one player on the team, they must have
                    # been the hitter of the ball.
                    if len(player_actor_ids) == 1:
                        car = player_cars[player_actor_ids[0]]

                        print(index, 'player position data', actor_positions[car])
                        print(index, 'ball position data', actor_positions[ball_actor_id])
                        print(index, 'distance', distance(actor_positions[car], actor_positions[ball_actor_id]))

                        last_hits[hit_team_num] = actor_positions[car]
                    elif len(player_actor_ids) == 0:
                        pprint(actors)
                        pprint(actors[2]['properties'])
                        return

                    print('')

                    # Clean up the actor positions.
                    actor_positions_copy = actor_positions.copy()
                    for actor_position in actor_positions_copy:
                        found = False

                        for car in player_cars:
                            if actor_position == player_cars[car]:
                                found = True

                        if not found:
                            del actor_positions[actor_position]

                # if replication['state'] == 'opening' and replication['actor_id'] in actors:
                #     print('now setting', replication['actor_id'])
                #     actors[replication['actor_id']] = replication
