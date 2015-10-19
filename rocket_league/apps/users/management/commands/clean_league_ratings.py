from django.core.management.base import BaseCommand

from ...models import LeagueRating


class Command(BaseCommand):

    def handle(self, *args, **options):
        steam_ids = LeagueRating.objects.all().distinct('steamid').values_list('steamid', flat=True).order_by()

        for steam_id in steam_ids:
            # Get the LeagueRating objects for this user.
            ratings = LeagueRating.objects.filter(
                steamid=steam_id,
            )
            print 'Working on', steam_id

            duels = None
            doubles = None
            solo_standard = None
            standard = None

            for rating in ratings:
                if (
                    rating.duels == duels and
                    rating.doubles == doubles and
                    rating.solo_standard == solo_standard and
                    rating.standard == standard
                ):
                    rating.delete()
                else:
                    duels = rating.duels
                    doubles = rating.doubles
                    solo_standard = rating.solo_standard
                    standard = rating.standard
