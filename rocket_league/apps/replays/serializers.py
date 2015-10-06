from .models import Goal, Map, Player, Replay

from rest_framework.serializers import HyperlinkedModelSerializer


class GoalSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Goal
        fields = ['url', 'replay', 'player', 'number', 'frame', 'goal_time']


class PlayerSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Player
        fields = ['url', 'replay', 'player_name', 'team']


class MapSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = Map


class ReplaySerializer(HyperlinkedModelSerializer):

    goal_set = GoalSerializer(
        many=True,
        read_only=True,
    )

    player_set = PlayerSerializer(
        many=True,
        read_only=True,
    )

    map = MapSerializer(
        many=False,
        read_only=True,
    )

    class Meta:
        model = Replay
        fields = ["url", "file", "replay_id", "player_name", "player_team",
                  "server_name", "timestamp", "team_sizes", "team_0_score",
                  "team_1_score", "match_type", "keyframe_delay",
                  "max_channels", "max_replay_size_mb", "num_frames",
                  "record_fps", "processed", "map", "player_set", "goal_set",
                  "lag_report_url", "match_length", "get_absolute_url"]

        depth = 1

    def validate(self, attrs):
        instance = Replay(**attrs)
        instance.clean()
        return attrs
