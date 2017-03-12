import os

import requests
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from rest_framework.authtoken.models import Token
from rlapi.client import RocketLeagueAPI
from social.apps.django_app.default.fields import JSONField
from social.apps.django_app.default.models import UID_LENGTH
from social.backends.steam import USER_INFO

from ..replays.models import PLATFORM_STEAM, PLATFORMS_MAPPINGS


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
        # This method will return the ratings for each of the platforms that the
        # user has associated with their account.  For most people this will only
        # be one, but it's useful to handle all cases regardless.

        accounts = []

        if self.has_steam_connected():
            accounts.append((PLATFORMS_MAPPINGS['steam'], self.user.social_auth.get(provider='steam').uid))

        account_data = {}
        for platform, online_id in accounts:
            account_data[platform] = LeagueRating.objects.filter(
                platform=platform,
                online_id=online_id,
            ).order_by('playlist')

        return account_data

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
            return reverse('users:player', kwargs={
                'platform': 'steam',
                'player_id': self.user.social_auth.get(provider='steam').uid
            })

        return reverse('users:profile', kwargs={
            'username': self.user.username
        })


class LeagueRatingManager(models.Manager):

    def filter_or_request(self, **kwargs):
        original_platform = kwargs['platform']
        kwargs['platform'] = PLATFORMS_MAPPINGS[original_platform]

        objects = self.filter(**kwargs)

        if objects:
            return objects

        kwargs['platform'] = original_platform

        # Get the rating from the API.
        rl = RocketLeagueAPI(os.getenv('ROCKETLEAGUE_API_KEY'))
        player = rl.get_player_skills(kwargs['platform'], kwargs['online_id'])[0]

        if kwargs['platform'] == PLATFORM_STEAM:
            online_id = player['user_id']
        else:
            online_id = player['user_name']

        timestamp = now()
        objects = []

        for playlist_data in player['player_skills']:
            obj, _ = LeagueRating.objects.update_or_create(
                platform=kwargs['platform'],
                online_id=online_id,
                playlist=playlist_data['playlist'],
                defaults={
                    'skill': playlist_data['skill'],
                    'matches_played': playlist_data['matches_played'],
                    'tier': playlist_data['tier'],
                    'tier_max': playlist_data['tier_max'],
                    'division': playlist_data['division'],
                    'timestamp': timestamp,
                }
            )

            objects.append(obj)

        return objects

    # {'online_id': '76561198181829054', 'platform': '1', 'playlist': 1}
    def get_or_request(self, *args, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            if (
                'playlist' not in kwargs or
                    'online_id' not in kwargs or
                    'platform' not in kwargs or
                    kwargs['playlist'] not in settings.RANKED_PLAYLISTS
            ):
                raise

            # Get the rating from the API.
            rl = RocketLeagueAPI(os.getenv('ROCKETLEAGUE_API_KEY'))
            player = rl.get_player_skills(PLATFORMS_MAPPINGS[kwargs['platform']], kwargs['online_id'])[0]

            if kwargs['platform'] == PLATFORM_STEAM:
                online_id = player['user_id']
            else:
                online_id = player['user_name']

            timestamp = now()
            return_obj = None

            for playlist_data in player['player_skills']:
                obj, _ = LeagueRating.objects.update_or_create(
                    platform=kwargs['platform'],
                    online_id=online_id,
                    playlist=playlist_data['playlist'],
                    defaults={
                        'skill': playlist_data['skill'],
                        'matches_played': playlist_data['matches_played'],
                        'tier': playlist_data['tier'],
                        'tier_max': playlist_data['tier_max'],
                        'division': playlist_data['division'],
                        'timestamp': timestamp,
                    }
                )

                if playlist_data['playlist'] == kwargs['playlist']:
                    return_obj = obj

            if return_obj:
                return return_obj
        raise


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

    objects = LeagueRatingManager()

    def __str__(self):
        return 'Platform: {}, Online ID: {}, Playlist: {}, Tier: {}'.format(
            self.platform,
            self.online_id,
            self.playlist,
            self.tier,
        )

    class Meta:
        ordering = ['-timestamp']
        unique_together = [['platform', 'online_id', 'playlist']]


class PlayerStatsManager(models.Manager):

    # {'online_id': '76561198181829054', 'platform': '1', 'playlist': 1}
    def get_or_request(self, *args, **kwargs):
        try:
            return self.get(**kwargs)
        except self.model.DoesNotExist:
            online_id = kwargs.get('online_id', None)
            platform = kwargs.get('platform', None)

            if not online_id or not platform:
                raise

            if platform == 'steam':
                online_id = int(online_id)

            # Get the rating from the API.
            rl = RocketLeagueAPI(os.getenv('ROCKETLEAGUE_API_KEY'))
            stats = rl.get_stats_values_for_user(platform, online_id)

            obj, _ = PlayerStats.objects.update_or_create(
                platform=platform,
                online_id=online_id,
                defaults=stats[online_id]
            )

            return obj

        raise


class PlayerStats(models.Model):

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

    wins = models.PositiveIntegerField(
        default=0,
    )

    assists = models.PositiveIntegerField(
        default=0,
    )

    goals = models.PositiveIntegerField(
        default=0,
    )

    shots = models.PositiveIntegerField(
        default=0,
    )

    mvps = models.PositiveIntegerField(
        default=0,
    )

    saves = models.PositiveIntegerField(
        default=0,
    )

    objects = PlayerStatsManager()


User.token = property(lambda u: Token.objects.get_or_create(user=u)[0])
User.profile = property(lambda u: Profile.objects.get_or_create(user=u)[0])


# Used for caching Steam data for users who don't have accounts.
class SteamCache(models.Model):

    uid = models.CharField(
        max_length=UID_LENGTH,
        db_index=True,
    )

    extra_data = JSONField(default=b'{}')
