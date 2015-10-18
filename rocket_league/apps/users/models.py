from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Max
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

from datetime import datetime
from rest_framework.authtoken.models import Token
import requests
from social.backends.steam import USER_INFO

from datetime import timedelta


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

    def rating_diff(self):
        # Do we have ratings from today as well as yesterday?
        yesterdays_rating = self.user.leaguerating_set.filter(
            timestamp__startswith=now().date() - timedelta(days=1),
        ).aggregate(
            Max('duels'),
            Max('doubles'),
            Max('solo_standard'),
            Max('standard'),
        )

        todays_ratings = self.user.leaguerating_set.filter(
            timestamp__startswith=now().date(),
        ).aggregate(
            Max('duels'),
            Max('doubles'),
            Max('solo_standard'),
            Max('standard'),
        )

        response = {}

        if todays_ratings['duels__max'] and yesterdays_rating['duels__max']:
            response[settings.PLAYLISTS['RankedDuels']] = todays_ratings['duels__max'] - yesterdays_rating['duels__max']

        if todays_ratings['doubles__max'] and yesterdays_rating['doubles__max']:
            response[settings.PLAYLISTS['RankedDoubles']] = todays_ratings['doubles__max'] - yesterdays_rating['doubles__max']

        if todays_ratings['solo_standard__max'] and yesterdays_rating['solo_standard__max']:
            response[settings.PLAYLISTS['RankedSoloStandard']] = todays_ratings['solo_standard__max'] - yesterdays_rating['solo_standard__max']

        if todays_ratings['standard__max'] and yesterdays_rating['standard__max']:
            response[settings.PLAYLISTS['RankedStandard']] = todays_ratings['standard__max'] - yesterdays_rating['standard__max']

        return response

    def has_steam_connected(self):
        try:
            self.user.social_auth.get(provider='steam')
            return True
        except:
            return False

    def steam_info(self):
        steam = self.user.social_auth.get(provider='steam')

        # Have we updated this profile recently?
        if 'last_updated' in steam.extra_data:
            # Parse the last updated date.
            last_date = parse_datetime(steam.extra_data['last_updated'])

            seconds_ago = (now() - last_date).seconds

            # 3600 seconds = 1 hour
            if seconds_ago < 3600:
                return steam.extra_data['player']

        try:
            player = requests.get(USER_INFO, params={
                'key': settings.SOCIAL_AUTH_STEAM_API_KEY,
                'steamids': steam.uid
            }).json()

            if len(player['response']['players']) > 0:
                steam.extra_data = {
                    'player': player['response']['players'][0],
                    'last_updated': now().isoformat(),
                }
                steam.save()
        except:
            pass

        return steam.extra_data['player']


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


User.token = property(lambda u: Token.objects.get_or_create(user=u)[0])
