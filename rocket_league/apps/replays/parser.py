import json
import os
import subprocess

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from pyrope import Replay


class Parser(object):

    def __init__(self, parse_netstream=False, obj=None):
        if not parse_netstream:
            self.replay = Replay(obj.file.read())
            self.replay_id = self.replay.header['Id']

            # Convert the Pyrope format into the Octane format.
            replay_temp = {
                'meta': {
                    'properties': self.replay.header
                }
            }

            if 'PlayerStats' in replay_temp['Metadata']:
                for index, player in enumerate(replay_temp['Metadata']['PlayerStats']):
                    replay_temp['Metadata']['PlayerStats'][index]['Platform'] = player['Platform']['OnlinePlatform']

            self.replay = replay_temp
        else:
            if settings.DEBUG:
                self.replay = json.loads(subprocess.check_output('octane-binaries/octane-*-osx {}'.format(obj.file.path), shell=True).decode('utf-8'))
            else:
                # Download the file from S3.
                command = 'wget {} -qO /tmp/{}'.format(
                    obj.file.url,
                    obj.replay_id,
                )

                os.system(command)

                self.replay = json.loads(subprocess.check_output('octane-binaries/octane-*-linux /tmp/{}'.format(obj.replay_id), shell=True).decode('utf-8'))

                os.remove('/tmp/{}'.format(obj.replay_id))

            self.replay_id = self.replay['Metadata']['Id']

        self.actor_metadata = {}
        self.player_actor_ids = []
        self.goal_metadata = {}
        self.match_metadata = {}
        self.team_metadata = {}
        self.actors = {}
        self.cars = {}
        self.boost_data = {}
        self.heatmap_json_filename = None
        self.disabled_frame_ranges = []

        assert len(self.team_metadata) == 0

        heatmap_json_filename = 'uploads/replay_json_files/{}.json'.format(self.replay_id)
        location_json_filename = 'uploads/replay_location_json_files/{}.json'.format(self.replay_id)

        if not parse_netstream:
            return

        self._get_actors()

        # If the number of goals in the header doesn't match the number of goals
        # in the game, try to get the missing goal data from the netstream.

        """
         ('3e_Team1',
          {'actor_id': 3,
           'class_name': 'Archetypes.Teams.Team1',
           'properties': {'Engine.TeamInfo:Score': 1},
           'new': False,
           'startpos': 2053839}),
               """
        if len(self.replay['Metadata'].get('Goals', [])) < self.replay['Metadata'].get('Team0Score', 0) + self.replay['Metadata'].get('Team1Score', 0):
            for index, frame in enumerate(self.replay['Frames']):
                for actor_id, actor in {**frame['Spawned'], **frame['Updated']}.items():
                    if 'properties' not in actor:
                        continue

                    if (
                        'Engine.TeamInfo:Score' in actor['properties'] and
                        'TAGame.Team_TA:GameEvent' not in actor['properties'] and
                        actor['Name'].startswith('Archetypes.Teams.Team')
                    ):
                        if 'Goals' not in self.replay['Metadata']:
                            self.replay['Metadata']['Goals'] = []

                        self.replay['Metadata']['Goals'].append({
                            'PlayerName': 'Unknown player (own goal?)',
                            'PlayerTeam': actor['Name'].replace('Archetypes.Teams.Team', ''),
                            'frame': index
                        })

        # Extract the goal information.
        if 'Goals' in self.replay['Metadata']:
            for goal in self.replay['Metadata']['Goals']:
                self._extract_goal_data(goal['frame'])

        if 'NumFrames' in self.replay['Metadata']:
            assert len(self.team_metadata) == 2

        for player in self.actors.copy():
            # Get their position data.
            if 'type' not in self.actors[player]:
                continue

            if self.actors[player]['type'] == 'player':
                self.actors[player]['position_data'] = self._get_player_position_data(player)
            elif self.actors[player]['type'] == 'ball':
                if 'ball' not in self.actors:
                    self.actors['ball'] = {
                        'type': 'ball',
                        'position_data': {}
                    }

                ball_data = self._get_player_position_data(player)

                self.actors['ball']['position_data'] = {
                    **self.actors['ball']['position_data'],
                    **ball_data
                }

                del self.actors[player]

        # Compress the location data per (player) actor.
        compressed_data = {}

        for actor in self.actors:
            if 'type' not in self.actors[actor]:
                continue

            compressed_data[actor] = {}

            current_key = ''
            key = ''

            keys = self.actors[actor]['position_data'].keys()

            if len(keys) == 0:
                continue

            for frame in range(min(keys), max(keys)):
                if frame in self.actors[actor]['position_data']:
                    data = self.actors[actor]['position_data'][frame]
                    key = '{},{}'.format(data['x'], data['y'])

                if key == current_key:
                    compressed_data[actor][key] += 1
                else:
                    if key not in compressed_data[actor]:
                        compressed_data[actor][key] = 1
                    else:
                        compressed_data[actor][key] += 1

            assert sum([i[1] for i in compressed_data[actor].items()]) == max(self.actors[actor]['position_data'], key=int) - min(self.actors[actor]['position_data'], key=int)

        if default_storage.exists(heatmap_json_filename):
            default_storage.delete(heatmap_json_filename)

        heatmap_json_filename = default_storage.save(heatmap_json_filename, ContentFile(json.dumps(compressed_data, separators=(',', ':'))))

        self.heatmap_json_filename = heatmap_json_filename

        # Advanced replay parsing.
        # Restructure the data so that it's chunkable.
        frame_data = []

        for frame in range(self.replay['Metadata'].get('NumFrames', 0)):
            frame_dict = {
                'time': self.replay['Frames'][frame]['Time'],
                'actors': []
            }

            for player in self.actors:
                position_data = self.actors[player]['position_data']

                if frame in position_data:
                    frame_dict['actors'].append({
                        'id': player,
                        'type': self.actors[player].get('type', 'ball'),
                        **position_data[frame]
                    })

            frame_data.append(frame_dict)

        if default_storage.exists(location_json_filename):
            default_storage.delete(location_json_filename)

        self._get_boost_data()
        self._get_seconds_remaining()

        small_actors = {}

        for key, value in self.actors.items():
            small_actors[key] = value

            del small_actors[key]['position_data']

        final_data = {
            'frame_data': frame_data,
            'goals': self.replay['Metadata'].get('Goals', []),
            'boost': self.boost_data,
            'seconds_mapping': self.seconds_mapping,
            'actors': self.actors,
            'teams': self.team_metadata
        }

        location_json_filename = default_storage.save(location_json_filename, ContentFile(json.dumps(final_data, separators=(',', ':'))))
        self.location_json_filename = location_json_filename

    def _get_match_metadata(self, frame):
        # Search through the frames looking for some game replication info.
        game_info = [
            value for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items()
            if (
                'GameReplicationInfoArchetype' in value.get('Name', '') and
                'Engine.GameReplicationInfo:ServerName' in value
            )
        ]

        if not game_info:
            return

        game_info = game_info[0]['properties']

        self.match_metadata = {
            'server_name': game_info['Engine.GameReplicationInfo:ServerName'],
            'playlist': game_info.get('ProjectX.GRI_X:ReplicatedGamePlaylist', 0)
        }

    def _get_team_metadata(self, frame):
        # Search through the frame looking for team info.
        team_info = [
            (actor_id, value) for actor_id, value in frame['Spawned'].items()
            if 'Archetypes.Teams.Team' in value.get('Name', '')
        ]

        if not team_info:
            return

        for team in team_info:
            self.team_metadata[team[0]] = team[1]['Name'].replace('Archetypes.Teams.Team', '')

    def _extract_goal_data(self, base_index, search_index=None, iteration=None):
        if not iteration:
            iteration = 1

        # If the player name is unique within the actor set, then don't bother
        # searching through frames for the data.
        for goal in self.replay['Metadata']['Goals']:
            if goal['frame'] == base_index:
                player = [
                    actor_id
                    for actor_id, data in self.actors.items()
                    if data['type'] == 'player' and data['name'] == goal['PlayerName']
                ]

                if len(player) == 1:
                    self.goal_metadata[base_index] = player[0]
                    return

                # We found the goal we wanted, we just couldn't find the player,
                # but break out early as a minor optimisation.
                break

        if not search_index:
            search_index = base_index

            if base_index >= len(self.replay['Frames']):
                search_index = base_index - 1

        frame = self.replay['Frames'][search_index]

        scorer = None

        if frame:
            players = [
                value
                for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items()
                if value.get('Name', '') == 'TAGame.Default__PRI_TA'
            ]

            # Figure out who scored.
            for value in players:
                if 'TAGame.PRI_TA:MatchGoals' in value:
                    scorer = value['actor_id']
                    break

                if 'TAGame.PRI_TA:MatchAssists' in value:
                    # print('we have the assister!', value['actor_id'])
                    pass

        # Search in the closest frames, then gradually expand the search.
        if scorer is None:
            if search_index < base_index - 100:
                print('Unable to find goal for frame', base_index)
                return

            if iteration >= 100:
                print('Unable to find goal for frame', base_index)
                return

            if search_index == base_index:
                next_index = base_index - 1
            elif search_index - base_index < 0:
                next_index = base_index + abs(search_index - base_index)
            elif search_index - base_index > 0:
                next_index = base_index + (search_index - base_index + 1) * -1

            if next_index >= len(self.replay['Frames']):
                if next_index < 0:
                    next_index = abs(search_index) + 1
                else:
                    next_index = search_index - 1

            self._extract_goal_data(base_index, next_index, iteration + 1)
            return

        self.goal_metadata[base_index] = scorer

    def _get_actors(self):
        for frame in self.replay['Frames']:
            # We can attempt to get the match metadata during this loop and
            # save us having to loop the netstream more than once.
            if not self.match_metadata:
                self._get_match_metadata(frame)

            if len(self.team_metadata) < 2:
                self._get_team_metadata(frame)

            # Find the player actor objects.
            players = [
                (actor_id, value)
                for actor_id, value in frame['Spawned'].items()
                if value.get('Name', '') == 'TAGame.Default__PRI_TA'
            ]

            for actor_id, value in players:
                if actor_id not in self.player_actor_ids:
                    self.player_actor_ids.append(actor_id)

                """
                Example `value`:

                {'Engine.PlayerReplicationInfo:Ping': 24,
                 'Engine.PlayerReplicationInfo:PlayerID': 656,
                 'Engine.PlayerReplicationInfo:PlayerName': "AvD Sub'n",
                 'Engine.PlayerReplicationInfo:Team': (True, 6),
                 'Engine.PlayerReplicationInfo:UniqueId': (1, 76561198040631598, 0),
                 'Engine.PlayerReplicationInfo:bReadyToPlay': True,
                 'TAGame.PRI_TA:CameraSettings': {'dist': 270.0,
                                                  'fov': 107.0,
                                                  'height': 110.0,
                                                  'pitch': -2.0,
                                                  'stiff': 1.0,
                                                  'swiv': 4.300000190734863},
                 'TAGame.PRI_TA:ClientLoadout': (11, [23, 0, 613, 39, 752, 0, 0]),
                 'TAGame.PRI_TA:ClientLoadoutOnline': (11, 0, 0),
                 'TAGame.PRI_TA:PartyLeader': (1, 76561198071203042, 0),
                 'TAGame.PRI_TA:ReplicatedGameEvent': (True, 1),
                 'TAGame.PRI_TA:Title': 0,
                 'TAGame.PRI_TA:TotalXP': 9341290,
                 'TAGame.PRI_TA:bUsingSecondaryCamera': True
                 }
                 """

                if 'Engine.PlayerReplicationInfo:bWaitingPlayer' in value:
                    continue

                team_id = None

                if 'Engine.PlayerReplicationInfo:Team' in value:
                    team_id = value['Engine.PlayerReplicationInfo:Team']['contents'][1]

                if actor_id in self.actors:
                    if team_id is not None:
                        if self.actors[actor_id]['team'] != team_id:
                            if actor_id in self.actor_metadata:
                                self.actor_metadata[actor_id]['Engine.PlayerReplicationInfo:Team'] = value['Engine.PlayerReplicationInfo:Team']

                            if team_id != -1:
                                self.actors[actor_id]['team'] = team_id

                        if not self.actors[actor_id]['team'] or team_id == -1:
                            # self.actors[actor_id]['team'] = team_id
                            self.actors[actor_id]['left'] = index

                elif 'TAGame.PRI_TA:ClientLoadout' in value:
                    player_name = value.get('Engine.PlayerReplicationInfo:PlayerName', None)

                    self.actors[actor_id] = {
                        'type': 'player',
                        'join': index,
                        'left': self.replay['Metadata']['NumFrames'],
                        'name': player_name['contents'] if player_name else '',
                        'team': team_id,
                    }

                    if actor_id not in self.actor_metadata:
                        self.actor_metadata[actor_id] = value

                # See if our current data value has any new fields.
                if actor_id not in self.actor_metadata:
                    self.actor_metadata[actor_id] = value
                else:
                    for key, value in value.items():
                        if key not in self.actor_metadata[actor_id] or self.actor_metadata[actor_id].get(key, None) is None:
                            self.actor_metadata[actor_id][key] = value

            # Get the ball data (if any).
            ball = [
                value
                for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items()
                if (
                    value.get('Name', '') == 'Archetypes.Ball.Ball_Default' and
                    'TAGame.RBActor_TA:ReplicatedRBState' in value.get('properties', {})
                )
            ]

            if ball:
                ball = ball[0]

                if ball['actor_id'] not in self.actors and 'TAGame.RBActor_TA:ReplicatedRBState' in ball['properties']:
                    self.actors[ball['actor_id']] = {
                        'type': 'ball'
                    }

            # Get the camera data (if any)
            cameras = [
                value
                for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items()
                if value.get('Name', '') == 'TAGame.Default__CameraSettingsActor_TA' and
                'TAGame.CameraSettingsActor_TA:PRI' in value.get('properties', {}) and
                'TAGame.CameraSettingsActor_TA:ProfileSettings' in value.get('properties', {})
            ]

            if len(cameras) > 0:
                for camera in cameras:
                    actor_id = camera['properties']['TAGame.CameraSettingsActor_TA:PRI']['contents'][1]

                    if 'TAGame.PRI_TA:CameraSettings' not in self.actor_metadata[actor_id]:
                        self.actor_metadata[actor_id]['TAGame.PRI_TA:CameraSettings'] = camera['properties']['TAGame.CameraSettingsActor_TA:ProfileSettings']

            # Figure out if the cars are locked in position at this point.
            # TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining
            """
            {'actor_id': 3,
             'class_name': 'Archetypes.GameEvent.GameEvent_Soccar',
             'properties': {'TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining': 3,
                      'id': 3,
                      'state': 'existing'},
             'new': False,
             'open': True,
             'startpos': 2864065})
            """

            game_events = [
                value
                for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items()
                if value.get('Name', '') == 'Archetypes.GameEvent.GameEvent_Soccar' and
                'TAGame.GameEvent_TA:ReplicatedGameStateTimeRemaining' in value.get('properties', {})
            ]

            if len(game_events):
                for event in game_events:
                    if len(self.disabled_frame_ranges) == 0:
                        self.disabled_frame_ranges.append([])

                    if len(self.disabled_frame_ranges[-1]) == 2:
                        self.disabled_frame_ranges.append([])

                    self.disabled_frame_ranges[-1].append(index)

    def _get_boost_data(self):
        # 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount'

        # Do we have a new car object? Assign it to the user.
        """
        {'actor_id': 7,
         'class_name': 'Archetypes.Car.Car_Default',
         'properties': {'Engine.Pawn:PlayerReplicationInfo': (True, 4),
                  'TAGame.Car_TA:TeamPaint': {'CustomColorID': 90,
                                              'CustomFinishID': 270,
                                              'Team': 0,
                                              'TeamColorID': 3,
                                              'TeamFinishID': 270},
                  'TAGame.RBActor_TA:ReplicatedRBState': {'flag': False,
                                                          'pos': (0, -4608, 43),
                                                          'rot': (-1.000030518509476,
                                                                  -0.500015259254738,
                                                                  -1.000030518509476),
                                                          'vec1': (0, 0, -162),
                                                          'vec2': (0, 0, 0)},
                  'TAGame.Vehicle_TA:ReplicatedThrottle': 255},
         'new': False,
         'startpos': 4230}
        {'actor_id': 8,
         'class_name': 'Archetypes.CarComponents.CarComponent_Boost',
         'properties': {'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount': 85,
                  'TAGame.CarComponent_TA:Vehicle': (True, 7)},
         'new': False,
         'startpos': 4537}
         """

        self.boost_actors = {}
        self.cars = {}

        for index, frame in enumerate(self.replay['Frames']):
            for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items():
                # Get any cars.
                if value.get('Name', '') == 'Archetypes.Car.Car_Default':
                    if 'properties' not in value:
                        continue

                    if 'Engine.Pawn:PlayerReplicationInfo' in value:
                        player_id = value['Engine.Pawn:PlayerReplicationInfo']['contents'][1]
                        self.cars[actor_id] = player_id

                # Get any boost objects.
                if value.get('Name', '') == 'Archetypes.CarComponents.CarComponent_Boost':
                    if actor_id not in self.boost_actors:
                        self.boost_actors[actor_id] = {}

                    if 'properties' not in value:
                        continue

                    if 'TAGame.CarComponent_TA:Vehicle' in value:
                        car_id = value['TAGame.CarComponent_TA:Vehicle']['contents'][1]
                        self.boost_actors[actor_id] = car_id

                    if 'TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount' in value:
                        if actor_id not in self.boost_data:
                            self.boost_data[actor_id] = {}

                        boost_value = value['TAGame.CarComponent_Boost_TA:ReplicatedBoostAmount']['contents']

                        assert 0 <= boost_value <= 255, 'Boost value {} is not in range 0-255.'.format(boost_value)

                        self.boost_data[actor_id][index] = boost_value

        # Data structure:
        #
        # value key = booster id (in values)
        # booster id maps to a car (in actors)
        # cars map to players (in card)

        self.boost_data = {
            'values': self.boost_data,
            'actors': self.boost_actors,
            'cars': self.cars,
        }

    def _get_seconds_remaining(self):
        self.seconds_mapping = {}

        for index, frame in enumerate(self.replay['Frames']):
            for actor_id, value in {**frame['Spawned'], **frame['Updated']}.items():
                if 'properties' not in value:
                    continue

                if 'TAGame.GameEvent_Soccar_TA:SecondsRemaining' in value:
                    self.seconds_mapping[index] = value['TAGame.GameEvent_Soccar_TA:SecondsRemaining']['contents']

    def _get_player_position_data(self, player_id):
        player = self.actors[player_id]
        result = {}

        car_actor_obj = None

        # TODO: Refactor this to only loop the netstream once.
        if player['type'] == 'player':
            for index in range(player['join'], player['left']):
                try:
                    frame = self.replay['Frames'][index]
                except KeyError:
                    # Handle truncated network data.
                    break

                stop = False
                for pair in self.disabled_frame_ranges:
                    if len(pair) < 2:
                        continue

                    if pair[0] <= index <= pair[1]:
                        stop = True
                        break

                if stop:
                    continue
                # Give it away, give it away, give it away now..

                assert stop is False

                # First we need to find the player's car object.
                for actor_id, actor_obj in {**frame['Spawned'], **frame['Updated']}.items():
                    if 'properties' not in actor_obj:
                        continue

                    engine = actor_obj['properties'].get('Engine.Pawn:PlayerReplicationInfo')

                    # This is the correct object for this player.
                    if engine and engine['contents'][1] == player_id:
                        car_actor_obj = actor_obj['actor_id']

                    # If the actor we're looking at is the car object, then get the
                    # position and rotation data for this frame.
                    if actor_obj['actor_id'] == car_actor_obj:
                        state_data = actor_obj['properties'].get('TAGame.RBActor_TA:ReplicatedRBState')

                        if state_data:
                            x, y, z = state_data['contents'][1]
                            yaw, pitch, roll = state_data['contents'][2]

                            result[index] = {
                                'x': x,
                                'y': y,
                                'z': z,
                                'pitch': pitch,
                                'roll': roll,
                                'yaw': yaw
                            }

        elif player['type'] == 'ball':
            for index, frame in enumerate(self.replay['Frames']):
                stop = False
                for pair in self.disabled_frame_ranges:
                    if len(pair) < 2:
                        continue

                    if pair[0] <= index <= pair[1]:
                        stop = True
                        break

                if stop:
                    continue
                # Give it away, give it away, give it away now..

                assert stop is False

                # Does this actor exist in the frame data?
                for actor_id, actor_obj in {**frame['Spawned'], **frame['Updated']}.items():
                    if 'properties' not in actor_obj:
                        continue

                    if actor_obj['actor_id'] != player_id:
                        continue

                    if 'TAGame.RBActor_TA:ReplicatedRBState' not in actor_obj['properties']:
                        continue

                    if actor_obj['Name'] != 'Archetypes.Ball.Ball_Default':
                        continue

                    state_data = actor_obj['properties']['TAGame.RBActor_TA:ReplicatedRBState']

                    x, y, z = state_data['contents'][1]
                    yaw, pitch, roll = state_data['contents'][2]

                    result[index] = {
                        'x': x,
                        'y': y,
                        'z': z,
                        'pitch': pitch,
                        'roll': roll,
                        'yaw': yaw
                    }

        return result
