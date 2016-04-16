from rest_framework import serializers


class StreamDataSerializer(serializers.Serializer):

    games_played = serializers.IntegerField()
    wins = serializers.IntegerField()
    losses = serializers.IntegerField()
    win_percentage = serializers.FloatField()
    goal_assist_ratio = serializers.FloatField()

    average_goals = serializers.FloatField()
    average_assists = serializers.FloatField()
    average_saves = serializers.FloatField()
    average_shots = serializers.FloatField()

    show_games_played = serializers.BooleanField()
    show_wins = serializers.BooleanField()
    show_losses = serializers.BooleanField()
    show_win_percentage = serializers.BooleanField()
    show_goal_assist_ratio = serializers.BooleanField()
    show_average_goals = serializers.BooleanField()
    show_average_assists = serializers.BooleanField()
    show_average_saves = serializers.BooleanField()
    show_average_shots = serializers.BooleanField()

    limit_to = serializers.CharField()

    font = serializers.CharField()
    custom_font = serializers.CharField()
    font_size = serializers.IntegerField()
    text_color = serializers.CharField()
    transparent_background = serializers.BooleanField()
    background_color = serializers.CharField()
    text_shadow = serializers.BooleanField()
