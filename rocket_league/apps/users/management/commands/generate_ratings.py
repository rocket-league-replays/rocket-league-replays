from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ...models import LeagueRating

from social.apps.django_app.default.models import UserSocialAuth

from datetime import timedelta
from random import randrange


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        users = UserSocialAuth.objects.filter(
            provider='steam',
        )

        for user in users:
            # Get their latest rating.
            latest_rating = LeagueRating.objects.filter(
                user=user.user,
            )[:1]

            if latest_rating:
                ratings = {
                    'duels': latest_rating[0].duels,
                    'doubles': latest_rating[0].doubles,
                    'standard': latest_rating[0].standard,
                }
            else:
                ratings = {
                    'duels': 0,
                    'doubles': 0,
                    'standard': 0,
                }

            timestamp = now()

            for x in range(1000):
                # Choose which stat to change.
                choice = randrange(1, 4)
                if choice == 1:
                    stat = 'duels'
                elif choice == 2:
                    stat = 'doubles'
                else:
                    stat = 'standard'

                change = randrange(-5, 11)

                ratings[stat] += change

                if ratings[stat] <= 0:
                    ratings[stat] = 0

                obj = LeagueRating.objects.create(
                    user=user.user,
                    **ratings
                )

                obj.timestamp = timestamp
                obj.save()

                if x % 15 == 0:
                    timestamp = timestamp + timedelta(minutes=1140)
                else:
                    timestamp = timestamp + timedelta(minutes=5)
