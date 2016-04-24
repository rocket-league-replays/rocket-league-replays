from django.core.management.base import BaseCommand

from ...models import LeagueRating
from ....replays.models import Season


class Command(BaseCommand):

    """
    Delete all league ratings except for the last one for each user in each season.
    """

    def handle(self, *args, **options):
        steam_ids = LeagueRating.objects.distinct('steamid').order_by('steamid').values_list('steamid', flat=True)

        for season in Season.objects.all():
            for steam_id in steam_ids:
                ratings = LeagueRating.objects.filter(
                    steamid=steam_id,
                    season_id=season.pk,
                )

                if ratings.count() > 1:
                    LeagueRating.objects.filter(
                        steamid=steam_id,
                        season_id=season.pk,
                    ).exclude(
                        pk=ratings[0].pk
                    ).delete()
