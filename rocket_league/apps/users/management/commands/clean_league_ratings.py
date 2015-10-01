from django.core.management.base import BaseCommand

from social.apps.django_app.default.models import UserSocialAuth


class Command(BaseCommand):

    def handle(self, *args, **options):
        users = UserSocialAuth.objects.filter(
            provider='steam',
        )

        for user in users:
            # Get the LeagueRating objects for this user.
            ratings = user.user.leaguerating_set.all()
            print 'Working on', user

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
