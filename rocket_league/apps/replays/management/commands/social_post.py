from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.timezone import now

from ...models import Replay

from twython import Twython

import os
import random
import praw


class Command(BaseCommand):
    help = "Send out the most exciting replay of the day to Twitter."

    def handle(self, *args, **options):
        replay = Replay.objects.filter(
            timestamp__startswith=now().date()
        ).order_by('-excitement_factor')[:1]

        if not replay:
            return

        replay = replay[0]

        # Post to Twitter.
        if (
            'TWITTER_API_KEY' in os.environ and 'TWITTER_API_SECRET' in os.environ and
            'TWITTER_ACCESS_TOKEN' in os.environ and 'TWITTER_ACCESS_SECRET' in os.environ
        ):
            twitter = Twython(
                os.environ['TWITTER_API_KEY'],
                os.environ['TWITTER_API_SECRET'],
                os.environ['TWITTER_ACCESS_TOKEN'],
                os.environ['TWITTER_ACCESS_SECRET'],
            )

            status_strings = [
                'The most exciting match today was a {size}v{size} on {map}. Take a look! {url} #RocketLeague',
            ]

            twitter.update_status(status=random.choice(status_strings).format(
                size=replay.team_sizes,
                map=str(replay.map),
                url='http://{base_url}{replay_url}'.format(
                    base_url=settings.SITE_DOMAIN,
                    replay_url=replay.get_absolute_url(),
                )
            ))

        # Post to reddit.
        if 'REDDIT_USERNAME' in os.environ and 'REDDIT_PASSWORD' in os.environ:
            reddit = praw.Reddit(user_agent='RocketLeagueReplays.com posting as /u/RocketLeagueReplays. Written by /u/danielsamuels')
            reddit.login(os.environ['REDDIT_USERNAME'], os.environ['REDDIT_PASSWORD'])
            reddit.submit(
                'RocketLeagueReplays',
                now().strftime('Match of the Day - %d/%m/%Y'),
                url='http://{base_url}{replay_url}'.format(
                    base_url=settings.SITE_DOMAIN,
                    replay_url=replay.get_absolute_url(),
                )
            )
