from django.core.management.base import BaseCommand

from .....utils.unofficial_api import api_login, get_league_data

from social.apps.django_app.default.models import UserSocialAuth


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        users = UserSocialAuth.objects.filter(
            provider='steam',
        )

        headers = api_login()

        for user in users:
            if user.user.profile.can_update_ratings():
                get_league_data(user, headers)
