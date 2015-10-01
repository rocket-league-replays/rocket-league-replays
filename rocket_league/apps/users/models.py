from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Profile(models.Model):
    user = models.OneToOneField(User)

    def latest_ratings(self):
        ratings = self.user.leaguerating_set.all()[:1]

        if ratings:
            return {
                settings.PLAYLISTS['RankedDuels']: ratings[0].duels,
                settings.PLAYLISTS['RankedDoubles']: ratings[0].doubles,
                settings.PLAYLISTS['RankedSoloStandard']: ratings[0].solo_standard,
                settings.PLAYLISTS['RankedStandard']: ratings[0].standard,
            }


class LeagueRating(models.Model):

    user = models.ForeignKey(User)

    duels = models.PositiveIntegerField()

    doubles = models.PositiveIntegerField()

    solo_standard = models.PositiveIntegerField()

    standard = models.PositiveIntegerField()

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-timestamp']
