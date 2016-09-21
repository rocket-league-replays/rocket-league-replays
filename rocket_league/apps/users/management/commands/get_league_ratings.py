import os
import sys
from contextlib import contextmanager
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now
from social.apps.django_app.default.models import UserSocialAuth

from ....replays.models import (PLATFORM_PSN, PLATFORM_STEAM, PLATFORM_UNKNOWN,
                                PLATFORM_XBOX, PLATFORMS_MAPPINGS, Player)
from ....users.models import LeagueRating

from rlapi import RocketLeagueAPI

rl = RocketLeagueAPI(os.getenv('ROCKETLEAGUE_API_KEY'))


@contextmanager
def file_lock(lock_file):
    if os.path.exists(lock_file):
        print('Only one script can run at once. Script is locked with %s' % lock_file)
        sys.exit(-1)
    else:
        open(lock_file, 'w').write("1")
        try:
            yield
        finally:
            os.remove(lock_file)


class Command(BaseCommand):

    def handle(self, *args, **options):
        # Get all Steam IDs from Player objects, as well as from UserSocialAuth
        # objects.

        with file_lock('/tmp/get_league_ratings.lock'):
            # Fix any messed up platform records.
            """
            [
                '',
                '0',
                '1',
                '2',
                '4',
                'OnlinePlatform_Dingo',
                'OnlinePlatform_PS4',
                'OnlinePlatform_Steam',
                'OnlinePlatform_Unknown',
                'Xbox',
                "{'Value': ['OnlinePlatform', 'OnlinePlatform_Dingo']}",
                "{'Value': ['OnlinePlatform', 'OnlinePlatform_PS4']}",
                "{'Value': ['OnlinePlatform', 'OnlinePlatform_Unknown']}",
                None
            ]
            """

            # Are there any automatic corrections we can make?
            Player.objects.filter(
                platform__in=["{'Value': ['OnlinePlatform', 'OnlinePlatform_Steam']}", "OnlinePlatform_Steam"]
            ).update(platform=PLATFORM_STEAM)

            Player.objects.filter(
                platform__in=["{'Value': ['OnlinePlatform', 'OnlinePlatform_Dingo']}", "OnlinePlatform_Dingo", 'Xbox']
            ).update(platform=PLATFORM_XBOX)

            Player.objects.filter(
                platform__in=["{'Value': ['OnlinePlatform', 'OnlinePlatform_PS4']}", "OnlinePlatform_PS4"]
            ).update(platform=PLATFORM_PSN)

            Player.objects.filter(
                platform__in=["{'Value': ['OnlinePlatform', 'OnlinePlatform_Unknown']}", "OnlinePlatform_Unknown", None, '']
            ).update(platform=PLATFORM_UNKNOWN)

            # Get any players which have featured in replays in the last 30 days.
            player_ids = Player.objects.filter(
                replay__timestamp__gte=now() - timedelta(days=7),
            ).exclude(
                Q(platform=None) |
                Q(platform='0') |
                Q(online_id='0') |
                Q(bot=True) |
                Q(spectator=True)
            ).distinct('platform', 'online_id').values_list('pk', 'platform', 'online_id').order_by('platform', 'online_id')

            for pk, platform, online_id in player_ids:
                print(pk, platform, online_id)
                print(LeagueRating.objects.filter(
                    platform=platform,
                    online_id=online_id,
                ))

                print(rl.get_player_skills(PLATFORMS_MAPPINGS[platform], online_id))

                """
                [
                    {
                        'user_name': 'Konge',
                        'player_skills': [
                            {
                                'playlist': 10,
                                'tier_max': 0,
                                'matches_played': 3,
                                'division': 0,
                                'skill': 93,
                                'tier': 0
                            },
                            {
                                'playlist': 11,
                                'tier_max': 5,
                                'matches_played': 66,
                                'division': 1,
                                'skill': 436,
                                'tier': 5
                            },
                            {
                                'playlist': 13,
                                'tier_max': 2,
                                'matches_played': 27,
                                'division': 2,
                                'skill': 178,
                                'tier': 2
                            }
                        ],
                        'user_id': 76561197960453675
                    }
                ]
                """
                exit()

            # print(player_ids)
            exit()

            social_auth_ids = UserSocialAuth.objects.filter(
                provider='steam',
            ).distinct('uid').values_list('uid', flat=True).order_by()

            steam_ids = []

            for steam_id in player_ids:
                steam_ids.append(str(steam_id))

            for steam_id in social_auth_ids:
                steam_ids.append(str(steam_id))

            steam_ids = set(steam_ids)

            # get_league_data(steam_ids)

            # call_command('clean_league_ratings')
