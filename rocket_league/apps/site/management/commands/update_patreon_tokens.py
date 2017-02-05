import os

import requests
from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):
        r = requests.post('http://api.patreon.com/oauth2/token', data={
            'grant_type': 'refresh_token',
            'refresh_token': os.getenv('PATREON_REFRESH_TOKEN'),
            'client_id': os.getenv('PATREON_CLIENT_ID'),
            'client_secret': os.getenv('PATREON_CLIENT_SECRET'),
        })

        tokens = r.json()

        print(tokens)

        with open(os.path.join(settings.SITE_ROOT, 'settings/secrets.py'), 'r') as f:
            settings_data = f.read()

        settings_data = settings_data.replace(os.getenv('PATREON_REFRESH_TOKEN'), tokens['refresh_token'])
        settings_data = settings_data.replace(os.getenv('PATREON_ACCESS_TOKEN'), tokens['access_token'])

        print(settings_data)

        with open('rocket_league/settings/secrets.py', 'w') as f:
            f.write(settings_data)
