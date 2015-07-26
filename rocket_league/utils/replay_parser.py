# This Python file uses the following encoding: utf-8
from ..apps.replays.models import Map

from datetime import datetime
from glob import glob
import re
import time


class ReplayParser(object):
    timestamp_regexp = re.compile(r'(\d{4}-\d{2}-\d{2}:\d{2}-\d{2})')
    map_name_regexp = re.compile(
        r'4D61704E616D65000D0000004E616D6550726F706572747900[0-9a-fA-F]{2}00000'
        r'000000000[0-9a-fA-F]{2}000000([0-9a-fA-F]+?)0005000000'
    )
    goal_regexp = re.compile(
        r'506C617965724E616D65000C00000053747250726F706572747900[0-9a-fA-F]{2}0'
        r'0000000000000[0-9a-fA-F]{2}000000([0-9a-fA-F]+?)000B000000506C6179657'
        r'25465616D000C000000496E7450726F70657274790004000000000000000([01]{1})'
        r'000000050000004E6F6E65'
    )
    id_regexp = re.compile(r'4964000C00000053747250726F706572747900250000000000000021000000([0-9a-fA-F]+?)0008000000')
    playername_regexp = re.compile(r'506C617965724E616D65000C00000053747250726F7065727479000A0000000000000006000000([0-9a-fA-F]+?)00')

    matchtype_regexp = re.compile(
        r'4D6174636854797065000D0000004E616D6550726F706572747900[0-9a-fA-F]{2}0'
        r'0000000000000[0-9a-fA-F]{2}000000([0-9a-fA-F]+?)000B000000'
    )
    server_regexp = re.compile(r'((?:EU|USE|USW|OCE)\d+-[A-Z][a-z]+)')

    player_team_regexp = re.compile(
        r'5072696D617279506C617965725465616D000C000000496E7450726F7065727479000'
        r'400000000000000([0-9a-fA-F]{2})'
    )

    def parse(self, obj):
        # Open the file and process it.
        with open(obj.file.path) as f:
            full_file = f.read()

        if not obj.replay_id:
            self.get_id(obj, full_file)

        if not obj.timestamp:
            self.get_timestamp(obj, full_file)

        if not obj.team_sizes:
            self.get_team_sizes(obj, full_file)

        if not obj.team_0_score or not obj.team_1_score:
            self.get_score(obj, full_file)

        self.get_goals(obj, full_file)
        assert len(obj.goals) == sum([obj.team_0_score, obj.team_1_score])

        if not obj.player_name:
            self.get_playername(obj, full_file)

        if not obj.match_type:
            self.get_matchtype(obj, full_file)

        if not obj.map:
            self.get_map(obj, full_file)

        if not obj.server_name:
            self.get_server_name(obj, full_file)

        self.get_player_team(obj, full_file)

        if not obj.player_team:
            obj.player_team = 0

        return obj

    def get_map(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.map_name_regexp.search(hex_line)
        if search:
            map_obj, created = Map.objects.get_or_create(
                slug=search.group(1).decode('hex'),
            )

            obj.map = map_obj

    def get_timestamp(self, obj, line):
        result = self.timestamp_regexp.search(line)

        if result:
            obj.timestamp = datetime.fromtimestamp(time.mktime(time.strptime(result.group(0), '%Y-%m-%d:%H-%M')))

    def get_team_sizes(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        # "TeamSize IntProperty"
        binary_search = '5465616D53697A65000C000000496E7450726F7065727479000400000000000000'
        string_index = hex_line.find(binary_search)

        if string_index != -1:
            # We have found the value.
            index = string_index + len(binary_search)
            obj.team_sizes = int(hex_line[index:index+2], 16)

    def get_score(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        # "Team0Score IntProperty"
        team_0_score = '5465616D3053636F7265000C000000496E7450726F7065727479000400000000000000'
        # "Team1Score IntProperty"
        team_1_score = '5465616D3153636F7265000C000000496E7450726F7065727479000400000000000000'

        team_0_index = hex_line.find(team_0_score)
        team_1_index = hex_line.find(team_1_score)

        if team_0_index != -1:
            # We have found the value.
            index = team_0_index + len(team_0_score)
            obj.team_0_score = int(hex_line[index:index+2], 16)

        if team_1_index != -1:
            # We have found the value.
            index = team_1_index + len(team_1_score)
            obj.team_1_score = int(hex_line[index:index+2], 16)

    def get_goals(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()
        obj.goals = []

        search = self.goal_regexp.findall(hex_line)

        if search:
            # Decode the name in each goal.
            for goal in search:
                obj.goals.append((goal[0].decode('hex'), goal[1]),)

    def get_id(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.id_regexp.search(hex_line)
        if search:
            obj.replay_id = search.group(1).decode('hex')

    def get_playername(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.playername_regexp.findall(hex_line)
        if search:
            obj.player_name = search[-1].decode('hex')

    def get_matchtype(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.matchtype_regexp.search(hex_line)
        if search:
            obj.match_type = search.group(1).decode('hex')

    def get_server_name(self, obj, line):
        search = self.server_regexp.search(line)

        if search:
            obj.server_name = search.group(0)

    def get_player_team(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.player_team_regexp.search(hex_line)

        if search:
            obj.player_team = search.group(1)
