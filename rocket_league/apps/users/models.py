from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now


class Profile(models.Model):
    user = models.OneToOneField(User)

    def can_update_ratings(self):
        # Get the last update.
        ratings = self.user.leaguerating_set.all()[:1]

        if not ratings:
            return True

        diff = now() - ratings[0].timestamp
        return diff.seconds > 300

    def latest_ratings(self):
        ratings = self.user.leaguerating_set.all()[:1]

        if ratings:
            return {
                settings.PLAYLISTS['RankedDuels']: ratings[0].duels,
                settings.PLAYLISTS['RankedDoubles']: ratings[0].doubles,
                settings.PLAYLISTS['RankedStandard']: ratings[0].standard,
            }


class LeagueRating(models.Model):

    user = models.ForeignKey(User)

    duels = models.PositiveIntegerField()

    doubles = models.PositiveIntegerField()

    standard = models.PositiveIntegerField()

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-timestamp']
