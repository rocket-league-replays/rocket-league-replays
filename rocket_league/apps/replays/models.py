from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from replay_parser import ReplayParser

from ..users.models import LeagueRating

import chardet
from datetime import datetime
import re
import struct
import time


class Map(models.Model):

    title = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    slug = models.CharField(
        max_length=100,
    )

    image = models.FileField(
        upload_to='uploads/files',
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return self.title or self.slug

    class Meta:
        ordering = ['title']


class Replay(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        db_index=True,
    )

    title = models.CharField(
        "replay name",
        max_length=32,
        blank=True,
        null=True,
    )

    file = models.FileField(
        upload_to='uploads/replay_files',
    )

    replay_id = models.CharField(
        "replay ID",
        max_length=100,
        blank=True,
        null=True,
    )

    player_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    player_team = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )

    map = models.ForeignKey(
        Map,
        blank=True,
        null=True,
        db_index=True,
    )

    server_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
    )

    timestamp = models.DateTimeField(
        blank=True,
        null=True,
    )

    team_sizes = models.PositiveIntegerField(
        blank=True,
        null=True,
        db_index=True,
    )

    team_0_score = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )

    team_1_score = models.IntegerField(
        default=0,
        blank=True,
        null=True,
    )

    match_type = models.CharField(
        max_length=7,
        blank=True,
        null=True,
    )

    # Parser V2 values.
    keyframe_delay = models.FloatField(
        blank=True,
        null=True,
    )

    max_channels = models.IntegerField(
        default=1023,
        blank=True,
        null=True,
    )

    max_replay_size_mb = models.IntegerField(
        "max replay size (MB)",
        default=10,
        blank=True,
        null=True,
    )

    num_frames = models.IntegerField(
        blank=True,
        null=True,
    )

    record_fps = models.FloatField(
        "record FPS",
        default=30.0,
        blank=True,
        null=True,
    )

    excitement_factor = models.FloatField(
        default=0.00,
    )

    show_leaderboard = models.BooleanField(
        default=False,
    )

    average_rating = models.PositiveIntegerField(
        blank=True,
        null=True,
        default=0,
    )

    processed = models.BooleanField(
        default=False,
    )

    def team_x_player_list(self, team):
        return [
            u"{}{}".format(
                player.player_name,
                " ({})".format(player.goal_set.count()) if player.goal_set.count() > 0 else '',
            ) for player in self.player_set.filter(
                team=team,
            )
        ]

    def team_x_players(self, team):
        return ', '.join(self.team_x_player_list(team))

    def team_0_players(self):
        return self.team_x_players(0)

    def team_1_players(self):
        return self.team_x_players(1)

    def team_0_player_list(self):
        return self.team_x_player_list(0)

    def team_1_player_list(self):
        return self.team_x_player_list(1)

    def player_pairs(self):
        return map(None, self.team_0_player_list(), self.team_1_player_list())

    def region(self):
        if not self.server_name:
            return 'N/A'

        match = re.search(settings.SERVER_REGEX, self.server_name).groups()
        return match[1]

    def lag_report_url(self):
        base_url = 'https://psyonixhr.wufoo.com/forms/game-server-performance-report'
        if not self.server_name:
            return base_url

        # Split out the server name.
        match = re.search(r'(EU|USE|USW|OCE|SAM)(\d+)(-([A-Z][a-z]+))?', self.server_name).groups()

        return "{}/def/field1={}&field2={}&field13={}".format(
            base_url,
            *match
        )

    def match_length(self):
        if not self.num_frames or not self.record_fps:
            return 'N/A'

        calculation = self.num_frames / self.record_fps
        minutes, seconds = divmod(calculation, 60)
        return '%d:%02d' % (
            int(minutes),
            int(seconds),
        )

    def calculate_excitement_factor(self):
        # Multiplers for use in factor tweaking.
        swing_rating_multiplier = 8
        goal_count_multiplier = 1.2

        # Calculate how the swing changed throughout the game.
        swing = 0
        swing_values = []

        for goal in self.goal_set.all():
            if goal.player.team == 0:
                swing -= 1
            else:
                swing += 1

            swing_values.append(swing)

        if self.team_0_score > self.team_1_score:
            # Team 0 won, but were they ever losing?
            deficit_values = filter(lambda x: x > 0, swing_values)

            if deficit_values:
                deficit = max(swing_values)
            else:
                deficit = 0

            score_min_def = self.team_0_score - deficit
        else:
            # Team 1 won, but were they ever losing?
            deficit_values = filter(lambda x: x < 0, swing_values)

            if deficit_values:
                deficit = abs(min(deficit_values))
            else:
                deficit = 0

            score_min_def = self.team_1_score - deficit

        if score_min_def != 0:
            swing_rating = float(deficit) / score_min_def * swing_rating_multiplier
        else:
            swing_rating = 0

        # Now we have the swing rating, adjust it by the total number of goals.
        # This gives us a "base value" for each replay and allows replays with
        # lots of goals but not much swing to get reasonable rating.
        swing_rating += (self.team_0_score + self.team_1_score) * goal_count_multiplier

        # Decay the score based on the number of days since the game was played.
        # This should keep the replay list fresh. Cap at a set number of days.
        days_ago = (now().date() - self.timestamp.date()).days

        day_cap = 75

        if days_ago > day_cap:
            days_ago = day_cap

        # Make sure we're not dividing by zero.
        if days_ago > 0:
            days_ago = float(days_ago)
            swing_rating -= swing_rating * days_ago / 100

        return swing_rating

    def calculate_average_rating(self):

        players = self.player_set.filter(
            platform='OnlinePlatform_Steam',
        ).exclude(
            online_id__isnull=True,
        )

        team_sizes = self.player_set.count() / 2

        num_player_ratings = 0
        total_player_ratings = 0

        for player in players:
            # Get the latest rating for this player.
            ratings = LeagueRating.objects.filter(
                steamid=player.online_id,
            ).exclude(
                duels=0,
                doubles=0,
                solo_standard=0,
                standard=0,
            )[:1]

            if len(ratings) > 0:
                rating = ratings[0]
            else:
                continue

            if team_sizes == 1:  # Duels
                total_player_ratings += rating.duels
                num_player_ratings += 1
            elif team_sizes == 2:  # Doubles
                total_player_ratings += rating.doubles
                num_player_ratings += 1
            elif team_sizes == 3:  # Standard or Solo Standard (can't tell which)
                total_player_ratings += (rating.solo_standard + rating.standard) / 2
                num_player_ratings += 1

        if num_player_ratings > 0:
            return total_player_ratings / num_player_ratings
        return 0

    def get_absolute_url(self):
        return reverse('replay:detail', kwargs={
            'pk': self.pk,
        })

    class Meta:
        ordering = ['-timestamp', '-pk']

    def __str__(self):
        return self.title or str(self.pk) or '[{}] {} {} game on {}. Final score: {}, Uploaded by {}.'.format(
            self.timestamp,
            '{size}v{size}'.format(size=self.team_sizes),
            self.match_type,
            self.map,
            '{}-{}'.format(self.team_0_score, self.team_1_score),
            self.player_name,
        )

    def clean(self):
        if self.pk:
            return

        if self.file:
            # Process the file.
            parser = ReplayParser()

            try:
                replay_data = parser.parse(self.file)['header']

                # Check if this replay has already been uploaded.
                replay = Replay.objects.filter(
                    replay_id=replay_data['Id']
                )

                if replay.count() > 0:
                    raise ValidationError(mark_safe("This replay has already been uploaded, <a href='{}'>you can view it here</a>.".format(
                        replay[0].get_absolute_url()
                    )))
            except struct.error:
                raise ValidationError("The file you selected does not seem to be a valid replay file.")

    def save(self, *args, **kwargs):
        super(Replay, self).save(*args, **kwargs)

        # Server name

        if self.file and not self.processed:
            # Process the file.
            parser = ReplayParser()
            data = parser.parse(self.file)['header']

            Goal.objects.filter(
                replay=self,
                frame__isnull=True,
            ).delete()

            Player.objects.filter(
                replay=self,
            ).delete()

            # If we have a stats table, pull in the data.
            if 'PlayerStats' in data:
                # We can show a leaderboard!
                self.show_leaderboard = True

                for player in data['PlayerStats']:
                    """
                    {
                        'OnlineID': 0,
                        'Name': 'Swabbie',
                        'Saves': 0,
                        'Platform': {
                            'OnlinePlatform': 'OnlinePlatform_Unknown'
                        },
                        'Score': 115,
                        'Goals': 1,
                        'Shots': 1,
                        'Team': 1,
                        'bBot': True,
                        'Assists': 0
                    }
                    """
                    Player.objects.get_or_create(
                        replay=self,
                        player_name=player['Name'].decode(chardet.detect(player['Name'])['encoding']),
                        platform=player['Platform'].get('OnlinePlatform', ''),
                        saves=player['Saves'],
                        score=player['Score'],
                        goals=player['Goals'],
                        shots=player['Shots'],
                        team=player['Team'],
                        assists=player['Assists'],
                        bot=player['bBot'],
                        online_id=player['OnlineID'],
                    )

            for index, goal in enumerate(data['Goals']):
                player, created = Player.objects.get_or_create(
                    replay=self,
                    player_name=goal['PlayerName'].decode(chardet.detect(goal['PlayerName'])['encoding']),
                    team=goal['PlayerTeam'],
                )

                Goal.objects.get_or_create(
                    replay=self,
                    number=index + 1,
                    player=player,
                    frame=goal['frame'],
                )

            data['PlayerName'] = data['PlayerName'].decode(
                chardet.detect(data['PlayerName'])['encoding']
            )

            player, created = Player.objects.get_or_create(
                replay=self,
                player_name=data['PlayerName'],
                team=data.get('PrimaryPlayerTeam', 0),
            )

            self.replay_id = data['Id']
            self.player_name = data['PlayerName']
            self.player_team = data.get('PrimaryPlayerTeam', 0)

            map_obj, created = Map.objects.get_or_create(
                slug=data['MapName'].lower(),
            )

            self.map = map_obj
            self.timestamp = datetime.fromtimestamp(
                time.mktime(
                    time.strptime(
                        data['Date'],
                        '%Y-%m-%d:%H-%M'
                    )
                )
            )
            self.team_sizes = data['TeamSize']
            self.team_0_score = data.get('Team0Score', 0)
            self.team_1_score = data.get('Team1Score', 0)
            self.match_type = data['MatchType']
            self.server_name = data.get('ServerName', '')

            # Parser V2 values
            self.keyframe_delay = data['KeyframeDelay']
            self.max_channels = data['MaxChannels']
            self.max_replay_size_mb = data['MaxReplaySizeMB']
            self.num_frames = data['NumFrames']
            self.record_fps = data['RecordFPS']

            self.excitement_factor = self.calculate_excitement_factor()
            self.average_rating = self.calculate_average_rating()
            self.processed = True
            self.save()


class Player(models.Model):

    replay = models.ForeignKey(
        Replay,
    )

    player_name = models.CharField(
        max_length=100,
        db_index=True,
    )

    team = models.IntegerField()

    # 1.06 data
    score = models.PositiveIntegerField(
        default=0,
        blank=True,
    )

    goals = models.PositiveIntegerField(
        default=0,
        blank=True,
    )

    shots = models.PositiveIntegerField(
        default=0,
        blank=True,
    )

    assists = models.PositiveIntegerField(
        default=0,
        blank=True,
    )

    saves = models.PositiveIntegerField(
        default=0,
        blank=True,
    )

    platform = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )

    online_id = models.BigIntegerField(
        blank=True,
        null=True,
        db_index=True,
    )

    bot = models.BooleanField(
        default=False,
    )

    user_entered = models.BooleanField(
        default=False,
    )

    def __unicode__(self):
        return u'{} on Team {}'.format(
            self.player_name,
            self.team,
        )

    class Meta:
        ordering = ('team', '-score')


class Goal(models.Model):

    replay = models.ForeignKey(
        Replay,
        db_index=True,
    )

    # Goal 1, 2, 3 etc..
    number = models.PositiveIntegerField()

    player = models.ForeignKey(
        Player,
        db_index=True,
    )

    frame = models.IntegerField(
        blank=True,
        null=True,
    )

    def goal_time(self):
        if not self.frame or not self.replay.record_fps:
            return 'N/A'

        calculation = self.frame / self.replay.record_fps
        minutes, seconds = divmod(calculation, 60)
        return '%d:%02d' % (
            int(minutes),
            int(seconds),
        )

    def __unicode__(self):
        return u'Goal {} by {}'.format(
            self.number,
            self.player,
        )

    class Meta:
        ordering = ['number']


class ReplayPack(models.Model):

    title = models.CharField(
        max_length=50,
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        db_index=True,
    )

    replays = models.ManyToManyField(
        Replay,
        blank=True,
    )

    file = models.FileField(
        upload_to='uploads/replaypack_files',
        blank=True,
        null=True,
    )

    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    last_updated = models.DateTimeField(
        auto_now=True,
    )

    def maps(self):
        maps = set([
            str(replay.map) for replay in self.replays.all()
        ])

        return ', '.join(maps)

    def goals(self):
        return sum([
            replay.team_0_score + replay.team_1_score
            for replay in self.replays.all()
        ])

    def players(self):
        players = set([
            player.player_name
            for replay in self.replays.all()
            for player in replay.player_set.all()
        ])

        return players

    def total_duration(self):
        calculation = sum([replay.num_frames for replay in self.replays.all()]) / 30
        minutes, seconds = divmod(calculation, 60)
        hours, minutes = divmod(minutes, 60)

        return '{} {}m {}s'.format(
            '{}h'.format(hours) if hours > 0 else '',
            int(minutes),
            int(seconds),
        )

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('replaypack:detail', kwargs={
            'pk': self.pk,
        })

    class Meta:
        ordering = ['-last_updated', '-date_created']
