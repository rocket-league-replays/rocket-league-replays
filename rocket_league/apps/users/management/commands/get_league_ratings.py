import os
import sys
from contextlib import contextmanager
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now
from rlapi.client import RocketLeagueAPI

from ....replays.models import (PLATFORM_PSN, PLATFORM_STEAM, PLATFORM_UNKNOWN,
                                PLATFORM_XBOX, PLATFORMS_MAPPINGS, Player)
from ....users.models import LeagueRating, PlayerStats

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


def chunks(input_list, chunk_length):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(input_list), chunk_length):
        yield input_list[i:i + chunk_length]


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            nargs='+',
            action='store',
            required=False,
        )

        parser.add_argument(
            '--online_id',
            type=str,
            nargs='+',
            action='store',
            required=False,
        )

    def handle_individual(self, platform, online_id):
        players = rl.get_player_skills(platform, online_id)

        if 'detail' in players:
            print(players['detail'])
            return

        print(players)

        timestamp = now()
        platform = PLATFORMS_MAPPINGS[platform]

        for player in players:
            if platform == PLATFORM_STEAM:
                online_id = player['user_id']
            else:
                online_id = player['user_name']

            for playlist_data in player['player_skills']:
                LeagueRating.objects.update_or_create(
                    platform=platform,
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

    def handle(self, *args, **options):
        if options['platform'] and options['online_id']:
            self.handle_individual(options['platform'][0], options['online_id'][0])
            exit()

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

            # Get any players which have featured in replays in the last X days.
            # Filter by one platform at a time so we can perform batch calls.
            base_query = Player.objects.filter(
                replay__timestamp__gte=now() - timedelta(days=31),
            ).exclude(
                Q(platform=None) |
                Q(platform='0') |
                Q(online_id='0') |
                Q(bot=True) |
                Q(spectator=True)
            ).distinct('platform', 'online_id').values_list(
                'pk', 'platform', 'online_id', 'player_name'
            ).order_by('platform', 'online_id')

            timestamp = now()

            for platform in [PLATFORM_STEAM, PLATFORM_PSN, PLATFORM_XBOX]:
                all_player_ids = base_query.filter(
                    platform=platform,
                )

                processed = 0

                # Loop over the IDs in chunks of 100.
                for player_ids in chunks(all_player_ids, 100):
                    processed += len(player_ids)

                    print('Processing {} {} players (making this {} of {} total).'.format(
                        len(player_ids),
                        PLATFORMS_MAPPINGS[platform],
                        processed,
                        len(all_player_ids),
                    ))

                    # The `online_id` value for Xbox players is an XUID which we
                    # can't do anything with, so instead we use the player_name.
                    if platform == PLATFORM_XBOX:
                        online_ids = [player[3] for player in player_ids]
                    elif platform == PLATFORM_STEAM:
                        online_ids = [int(player[2]) for player in player_ids]
                    else:
                        online_ids = [player[2] for player in player_ids]

                    players = rl.get_player_skills(PLATFORMS_MAPPINGS[platform], online_ids)

                    # While we're here, get their stats as well.
                    stats = rl.get_stats_values_for_user(PLATFORMS_MAPPINGS[platform], online_ids)

                    for player in players:
                        if platform == PLATFORM_STEAM:
                            online_id = player['user_id']
                        else:
                            online_id = player['user_name']

                        for playlist_data in player['player_skills']:
                            LeagueRating.objects.update_or_create(
                                platform=platform,
                                online_id=online_id,
                                playlist=playlist_data['playlist'],
                                defaults={
                                    'skill': playlist_data.get('skill') or 0,
                                    'matches_played': playlist_data.get('matches_played') or 0,
                                    'tier': playlist_data.get('tier') or 0,
                                    'tier_max': playlist_data.get('tier_max') or 0,
                                    'division': playlist_data.get('division') or 0,
                                    'timestamp': timestamp,
                                }
                            )

                        PlayerStats.objects.update_or_create(
                            platform=platform,
                            online_id=online_id,
                            defaults=stats[online_id]
                        )
