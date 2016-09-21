from datetime import timedelta

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Max
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from rest_framework.authtoken.models import Token
from social.apps.django_app.default.fields import JSONField
from social.apps.django_app.default.models import UID_LENGTH
from social.backends.steam import USER_INFO

from ..replays.models import Season, get_default_season


class Profile(models.Model):
    user = models.OneToOneField(User)

    patreon_email_address = models.EmailField(
        unique=True,
        blank=True,
        null=True,
    )

    twitter_username = models.CharField(
        b"Twitter username",
        max_length=100,
        blank=True,
        null=True,
    )

    twitch_username = models.CharField(
        b"Twitch.tv username",
        max_length=100,
        blank=True,
        null=True,
    )

    reddit_username = models.CharField(
        b"reddit username",
        max_length=100,
        blank=True,
        null=True,
    )

    youtube_url = models.URLField(
        b"YouTube URL",
        blank=True,
        null=True,
    )

    facebook_url = models.URLField(
        b"Facebook URL",
        blank=True,
        null=True,
    )

    stream_settings = JSONField(
        blank=True,
        null=True,
    )

    privacy = models.PositiveIntegerField(
        'replay privacy',
        choices=[
            (1, b'Private'),
            (2, b'Unlisted'),
            (3, b'Public')
        ],
        default=3,
    )

    def latest_ratings(self):
        if not self.has_steam_connected():
            return {}

        steam_id = self.user.social_auth.get(provider='steam').uid

        ratings = LeagueRating.objects.filter(
            steamid=steam_id,
            season_id=get_default_season(),
        )

        if ratings.count() > 1:
            LeagueRating.objects.filter(
                steamid=steam_id,
                season_id=get_default_season(),
            ).exclude(
                pk=ratings[0].pk
            ).delete()

        if ratings:
            return {
                settings.PLAYLISTS['RankedDuels']: ratings[0].duels,
                '{}_division'.format(settings.PLAYLISTS['RankedDuels']): ratings[0].duels_division,
                settings.PLAYLISTS['RankedDoubles']: ratings[0].doubles,
                '{}_division'.format(settings.PLAYLISTS['RankedDoubles']): ratings[0].doubles_division,
                settings.PLAYLISTS['RankedSoloStandard']: ratings[0].solo_standard,
                '{}_division'.format(settings.PLAYLISTS['RankedSoloStandard']): ratings[0].solo_standard_division,
                settings.PLAYLISTS['RankedStandard']: ratings[0].standard,
                '{}_division'.format(settings.PLAYLISTS['RankedStandard']): ratings[0].standard_division,
            }

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

    def has_had_trial(self):
        from ..site.models import PatronTrial

        return PatronTrial.objects.filter(
            user=self.user,
        ).count() > 0

    @property
    def clean_twitch_username(self):
        if 'twitch.tv' in self.twitch_username:
            return self.twitch_username.split('/')[-1]
        return self.twitch_username

    def get_absolute_url(self):
        if self.has_steam_connected():
            return reverse('users:steam', kwargs={
                'steam_id': self.user.social_auth.get(provider='steam').uid
            })

        return reverse('users:profile', kwargs={
            'username': self.user.username
        })


class LeagueRating(models.Model):

    """
    [
        {
            “user_name”: “Rocket_League1”,
            “player_skills”: [
                {
                    “playlist”: 10,
                    “skill”: 217,
                    “matches_played”: 2,
                    “tier”: 0,
                    “tier_max”: 0,
                    “division”: 0,
                }
            ]
        }
    ]
    """

    platform = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True,
    )

    online_id = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        db_index=True,
    )

    playlist = models.PositiveIntegerField(
        choices=[(int(v), bytes(k, 'utf8')) for k, v in settings.PLAYLISTS.items()],
        default=0,
    )

    skill = models.PositiveIntegerField(
        default=0,
    )

    matches_played = models.PositiveIntegerField(
        default=0,
    )

    tier = models.PositiveIntegerField(
        choices=[(k, v) for k, v in settings.TIERS.items()],
        default=0,
    )

    tier_max = models.PositiveIntegerField(
        choices=[(k, v) for k, v in settings.TIERS.items()],
        default=0,
    )

    division = models.PositiveIntegerField(
        choices=[(k, v) for k, v in settings.DIVISIONS.items()],
        default=0,
    )

    timestamp = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-timestamp']
        unique_together = [['platform', 'online_id', 'playlist']]


User.token = property(lambda u: Token.objects.get_or_create(user=u)[0])
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])


# Used for caching Steam data for users who don't have accounts.
class SteamCache(models.Model):

    uid = models.CharField(
        max_length=UID_LENGTH,
        db_index=True,
    )

    extra_data = JSONField(default=b'{}')
