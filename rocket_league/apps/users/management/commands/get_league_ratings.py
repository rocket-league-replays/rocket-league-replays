from django.core.management import call_command
from django.core.management.base import BaseCommand

from ....replays.models import Player
from .....utils.unofficial_api import get_league_data

from social.apps.django_app.default.models import UserSocialAuth


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        # Get all Steam IDs from Player objects, as well as from UserSocialAuth
        # objects.

        player_ids = Player.objects.filter(
            platform='OnlinePlatform_Steam',
        ).distinct('online_id').values_list('online_id', flat=True).order_by()

        social_auth_ids = UserSocialAuth.objects.filter(
            provider='steam',
        ).distinct('uid').values_list('uid', flat=True).order_by()

        steam_ids = set(list(player_ids) + list(social_auth_ids))

        get_league_data(steam_ids)

        call_command('clean_league_ratings')
