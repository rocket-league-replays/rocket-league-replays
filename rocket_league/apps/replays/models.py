from django.core.urlresolvers import reverse
from django.db import models

from ...utils.replay_parser import ReplayParser

from datetime import datetime
import re
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

    processed = models.BooleanField(
        default=False,
    )

    def team_x_player_list(self, team):
        return [
            "{}{}".format(
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

        match = re.search(r'(EU|USE|USW|OCE)(\d+)-([A-Z][a-z]+)', self.server_name).groups()
        return match[0]

    def lag_report_url(self):
        base_url = 'https://psyonixhr.wufoo.com/forms/game-server-performance-report'
        if not self.server_name:
            return base_url

        # Split out the server name.
        match = re.search(r'(EU|USE|USW|OCE)(\d+)-([A-Z][a-z]+)', self.server_name).groups()

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

    def get_absolute_url(self):
        return reverse('replay:detail', kwargs={
            'pk': self.pk,
        })

    class Meta:
        ordering = ['-timestamp', '-pk']

    def __str__(self):
        return '[{}] {} {} game on {}. Final score: {}, Uploaded by {}.'.format(
            self.timestamp,
            '{size}v{size}'.format(size=self.team_sizes),
            self.match_type,
            self.map,
            '{}-{}'.format(self.team_0_score, self.team_1_score),
            self.player_name,
        )

    def save(self, *args, **kwargs):
        super(Replay, self).save(*args, **kwargs)

        # Server name

        if self.file and not self.processed:
            # Process the file.
            parser = ReplayParser()
            data = parser.parse(self)

            Goal.objects.filter(
                replay=self,
                frame__isnull=True,
            ).delete()

            Player.objects.filter(
                replay=self,
            ).delete()

            for index, goal in enumerate(data['Goals']):
                player, created = Player.objects.get_or_create(
                    replay=self,
                    player_name=goal['PlayerName'],
                    team=goal['PlayerTeam'],
                )

                Goal.objects.get_or_create(
                    replay=self,
                    number=index + 1,
                    player=player,
                    frame=goal['frame'],
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
                slug=data['MapName'],
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

            self.processed = True
            self.save()


class Player(models.Model):

    replay = models.ForeignKey(
        Replay,
    )

    player_name = models.CharField(
        max_length=100,
    )

    team = models.IntegerField()

    def __unicode__(self):
        return u'{} on Team {}'.format(
            self.player_name,
            self.team,
        )


class Goal(models.Model):

    replay = models.ForeignKey(
        Replay,
    )

    # Goal 1, 2, 3 etc..
    number = models.PositiveIntegerField()

    player = models.ForeignKey(
        Player,
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
