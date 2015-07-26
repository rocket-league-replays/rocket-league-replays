# This Python file uses the following encoding: utf-8
from glob import glob
import re
import time


class Replay(object):
    id = None
    playername = None
    file_path = None
    map_name = None
    timestamp = None
    team_sizes = None
    matchtype = None
    score = (0, 0)
    goals = []
    team_0_players = []
    team_1_players = []

    def __init__(self, file_path):
        self.file_path = file_path

    def __str__(self):
        return '[{}] {} {} game on {}. Final score: {}, Uploaded by {}.'.format(
            time.strftime('%Y-%m-%d %H:%M', self.timestamp),
            '{size}v{size}'.format(size=self.team_sizes),
            self.matchtype,
            self.map_name,
            '{}-{}'.format(self.score[0], self.score[1]),
            self.playername,
        )


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

    def main(self, files):
        if not isinstance(files, list):
            raise TypeError("You must supply a list of file names.")

        for replay in files:
            obj = self.process_file(replay)
            print obj

    def process_file(self, path):
        # Create a new Replay object.
        obj = Replay(path)

        # Open the file and process it.
        with open(path) as f:
            for line in f:
                if not obj.id:
                    self.get_id(obj, line)

                if not obj.timestamp:
                    self.get_timestamp(obj, line)

                if not obj.team_sizes:
                    self.get_team_sizes(obj, line)

                if not obj.score[0] or not obj.score[1]:
                    self.get_score(obj, line)

            # To parse the goals we have to search the whole file.
            f.seek(0)
            self.get_goals(obj, f.read())
            assert len(obj.goals) == sum(obj.score)

            f.seek(0)
            if not obj.playername:
                self.get_playername(obj, f.read())

            f.seek(0)
            if not obj.matchtype:
                self.get_matchtype(obj, f.read())

            f.seek(0)
            if not obj.map_name:
                self.get_map(obj, f.read())

        return obj

    def get_map(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.map_name_regexp.search(hex_line)
        if search:
            obj.map_name = search.group(1).decode('hex')

    def get_timestamp(self, obj, line):
        result = self.timestamp_regexp.search(line)

        if result:
            obj.timestamp = time.strptime(result.group(0), '%Y-%m-%d:%H-%M')

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
            obj.score = (int(hex_line[index:index+2], 16), obj.score[1])

        if team_1_index != -1:
            # We have found the value.
            index = team_1_index + len(team_1_score)
            obj.score = (obj.score[0], int(hex_line[index:index+2], 16))

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
            obj.id = search.group(1).decode('hex')

    def get_playername(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.playername_regexp.search(hex_line)
        if search:
            obj.playername = search.group(1).decode('hex')

    def get_matchtype(self, obj, line):
        hex_line = "".join("{:02x}".format(ord(c)) for c in line).upper()

        search = self.matchtype_regexp.search(hex_line)
        if search:
            obj.matchtype = search.group(1).decode('hex')

if __name__ == '__main__':
    files = glob('replays/*.replay')

    parser = ReplayParser()
    parser.main(files)
    # print files[0]
    # parser.main(['replays/smaller2.replay'])
