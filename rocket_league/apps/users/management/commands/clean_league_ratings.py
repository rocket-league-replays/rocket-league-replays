from django.core.management.base import BaseCommand

from ...models import LeagueRating
from ....replays.models import Player

from social.apps.django_app.default.models import UserSocialAuth


class Command(BaseCommand):

    def handle(self, *args, **options):
        player_ids = Player.objects.filter(
            platform='OnlinePlatform_Steam',
        ).distinct('online_id').values_list('online_id', flat=True).order_by()

        social_auth_ids = UserSocialAuth.objects.filter(
            provider='steam',
        ).distinct('uid').values_list('uid', flat=True).order_by()

        steam_ids = set(list(player_ids) + list(social_auth_ids))

        # Delete any rows which contain a 0.
        LeagueRating.objects.filter(
            duels=0,
            doubles=0,
            solo_standard=0,
            standard=0,
        ).delete()

        for steam_id in steam_ids:
            # Get the LeagueRating objects for this user.
            ratings = LeagueRating.objects.filter(
                steamid=steam_id,
            )[:10]
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
