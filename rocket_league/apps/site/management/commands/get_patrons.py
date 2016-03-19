import os
from pprint import pprint
from urllib.parse import urlparse, parse_qs

import patreon
from django.core.management.base import BaseCommand

from ...models import Patron


class Command(BaseCommand):

    def process_pledges(self, data):
        processed = 0
        pledges = (pledge for pledge in data['data'] if pledge['type'] == 'pledge')

        patrons = {
            patron['id']: patron['attributes']
            for patron in data['included']
            if patron['type'] == 'user' and patron['id'] != '3014923'
        }

        for pledge in pledges:
            patron_id = pledge['relationships']['patron']['data']['id']
            patron = patrons[patron_id]

            Patron.objects.get_or_create(
                pledge_id=pledge['id'],
                defaults={
                    'pledge_amount': pledge['attributes']['amount_cents'],
                    'pledge_created': pledge['attributes']['created_at'],
                    'pledge_declined_since': pledge['attributes']['declined_since'],
                    'patron_id': patron_id,
                    'patron_email': patron['email'],
                    'patron_facebook': patron['facebook'],
                    'patron_twitter': patron['twitter'],
                    'patron_youtube': patron['youtube'],
                }
            )

            processed += 1

        return processed

    def handle(self, *args, **options):
        # oauth_client = patreon.OAuth(os.getenv('PATREON_CLIENT_ID'), os.getenv('PATREON_CLIENT_SECRET'))
        api_client = patreon.API(os.getenv('PATREON_ACCESS_TOKEN'))
        per_page = 20
        processed = 0

        pledges, cursor = api_client.fetch_page_of_pledges(318380, per_page, return_cursor=True)
        processed += self.process_pledges(pledges)

        while 'next' in pledges['links']:
            # Get the next page
            pledges, cursor = api_client.fetch_page_of_pledges(318380, per_page, cursor, return_cursor=True)
            processed += self.process_pledges(pledges)

        assert processed == pledges['meta']['count']
