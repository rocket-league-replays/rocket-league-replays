from django.core.management import call_command
from django.core.management.base import BaseCommand

from ...models import LeagueRating
from .....utils.unofficial_api import api_login, get_league_data


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        steam_ids = LeagueRating.objects.all().distinct('steamid').values_list('steamid', flat=True).order_by()

        headers = api_login()

        for steam_id in steam_ids:
            print 'Getting rating data for', steam_id
            get_league_data(steam_id, headers)

        call_command('clean_league_ratings')
