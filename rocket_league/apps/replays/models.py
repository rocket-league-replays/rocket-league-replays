from django.db import models


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

    processed = models.BooleanField(
        default=False,
    )

    class Meta:
        ordering = ['-timestamp']

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

        if self.file and not self.processed:
            # Imported here to avoid circular imports.
            from ...utils.replay_parser import ReplayParser

            # Process the file.
            parser = ReplayParser()
            parser.parse(self)

            for index, goal in enumerate(self.goals):
                player, created = Player.objects.get_or_create(
                    replay=self,
                    player_name=goal[0],
                    team=goal[1],
                )

                Goal.objects.get_or_create(
                    replay=self,
                    number=index + 1,
                    player=player,
                )

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

    def __unicode__(self):
        return u'Goal {} by {}'.format(
            self.number,
            self.player,
        )
