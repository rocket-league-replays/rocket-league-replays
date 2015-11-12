from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now

from rest_framework.authtoken.models import Token
import requests
from social.backends.steam import USER_INFO
from social.apps.django_app.default.fields import JSONField
from social.apps.django_app.default.models import UID_LENGTH

from datetime import timedelta


class Profile(models.Model):
    user = models.OneToOneField(User)

    def latest_ratings(self):
        if not self.has_steam_connected():
            return {}

        steam_id = self.user.social_auth.get(provider='steam').uid

        ratings = LeagueRating.objects.filter(
            steamid=steam_id,
        )[:1]

        if ratings:
            return {
                settings.PLAYLISTS['RankedDuels']: ratings[0].duels,
                settings.PLAYLISTS['RankedDoubles']: ratings[0].doubles,
                settings.PLAYLISTS['RankedSoloStandard']: ratings[0].solo_standard,
                settings.PLAYLISTS['RankedStandard']: ratings[0].standard,
            }

    def rating_diff(self):
        steam_id = self.user.social_auth.get(provider='steam').uid

        # Do we have ratings from today as well as yesterday?
        yesterdays_rating = LeagueRating.objects.filter(
            steamid=steam_id,
            timestamp__startswith=now().date() - timedelta(days=1),
        ).aggregate(
            Max('duels'),
            Max('doubles'),
            Max('solo_standard'),
            Max('standard'),
        )

        todays_ratings = LeagueRating.objects.filter(
            steamid=steam_id,
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

    def get_absolute_url(self):
        if self.has_steam_connected():
            return reverse('users:steam', kwargs={
                'steam_id': self.user.social_auth.get(provider='steam').uid
            })

        return reverse('users:profile', kwargs={
            'username': self.user.username
        })


class LeagueRating(models.Model):

    steamid = models.BigIntegerField(
        blank=True,
        null=True,
        db_index=True,
    )

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
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])


# Used for caching Steam data for users who don't have accounts.
class SteamCache(models.Model):

    uid = models.CharField(
        max_length=UID_LENGTH,
        db_index=True,
    )

    extra_data = JSONField()
