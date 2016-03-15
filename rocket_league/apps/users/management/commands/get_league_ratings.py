from django.core.management import call_command
from django.core.management.base import BaseCommand

from ....replays.models import Player
from .....utils.unofficial_api import get_league_data

from social.apps.django_app.default.models import UserSocialAuth

from contextlib import contextmanager
import os
import sys


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
            player_ids = Player.objects.filter(
                platform__in=['OnlinePlatform_Steam', '1'],
            ).distinct('online_id').values_list('online_id', flat=True).order_by()

            social_auth_ids = UserSocialAuth.objects.filter(
                provider='steam',
            ).distinct('uid').values_list('uid', flat=True).order_by()

            steam_ids = []

            for steam_id in player_ids:
                steam_ids.append(str(steam_id))

            for steam_id in social_auth_ids:
                steam_ids.append(str(steam_id))

            steam_ids = set(steam_ids)

            get_league_data(steam_ids)

            call_command('clean_league_ratings')
