import json
import logging
import os
import sys
import traceback
from contextlib import contextmanager

import requests
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ...models import Player, Replay

logger = logging.getLogger('rocket_league')


@contextmanager
def file_lock(lock_file, options):
    if options['replay_id']:
        lock_file = '{}.{}'.format(lock_file, options['replay_id'])

    if os.path.exists(lock_file):
        print('[{}] Only one script can run at once. Script is locked with {}'.format(
            now(),
            lock_file
        ))
        sys.exit(-1)
    else:
        open(lock_file, 'w').write("1")
        try:
            yield
        finally:
            os.remove(lock_file)


class Command(BaseCommand):
    help = "Generate location JSON files for replays which are missing it."

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('replay_id', nargs='?', type=int)

        # Named (optional) arguments
        parser.add_argument(
            '--patreon',
            action='store_true',
            dest='patreon',
            default=False,
            help='Only process replays which are eligible for extra display options.'
        )

    def handle(self, *args, **options):
        num_processed = 0

        with file_lock('/tmp/generate_heatmaps.lock', options):
            # Get any replays which don't have a location JSON file. Check if
            # each replay is eligible to have one.

            if options['replay_id']:
                replays = Replay.objects.filter(pk=options['replay_id'])
            else:
                # Get any replays which don't have a location JSON file.
                replays = Replay.objects.exclude(
                    crashed_heatmap_parser=True
                ).order_by('-timestamp', '-average_rating')

            for replay in replays:
                # To avoid the queue getting too backlogged, only process a few
                # replays at a time.
                if num_processed >= 25:
                    return

                if replay.replay_id and replay.file:
                    needs_processing = False

                    # Is this a Patreon-specific job? If so, skip any replays which
                    # aren't naturally eligible for the extra stuff.
                    if options['patreon']:
                        if replay.eligible_for_playback() and not replay.location_json_file:
                            needs_processing = True

                        if replay.eligible_for_boost_analysis() and replay.boostdata_set.count() == 0:
                            needs_processing = True
                    else:
                        if not replay.location_json_file:
                            needs_processing = True

                        if replay.boostdata_set.count() == 0:
                            needs_processing = True

                    if options['replay_id']:
                        needs_processing = True

                    # Have any of the players got vehicle data?
                    vehicle_data = Player.objects.filter(
                        replay_id=replay.pk
                    ).exclude(
                        vehicle_loadout__in=['"{}"', '{}']
                    )

                    if vehicle_data.count() == 0:
                        needs_processing = True

                    if not needs_processing:
                        continue

                    print('[{}] Processing {} - {}'.format(
                        now(),
                        replay.pk,
                        replay.replay_id
                    ))

                    try:
                        replay.processed = False
                        replay.save(parse_netstream=True)

                        replay.refresh_from_db()

                        replay_processed = True

                        if not replay.location_json_file:
                            replay_processed = False

                        if replay.boostdata_set.count() == 0:
                            replay_processed = False

                        if not replay_processed:
                            replay.crashed_heatmap_parser = True
                            replay.save()
                        else:
                            num_processed += 1

                    except Exception:
                        replay.crashed_heatmap_parser = True
                        replay.save()

                        print('[{}] Unable to process replay {}.'.format(now(), replay.pk))
                        print('[{}] {}'.format(now(), traceback.format_exc()))

                        try:
                            requests.post(settings.SLACK_URL, data={
                              'payload': json.dumps({
                                  'channel': '#cronjobs',
                                  'username': 'Cronjob Bot',
                                  'icon_emoji': ':timer_clock:',
                                  'text': 'Unable to process replay {}.'.format(replay.pk)
                              })
                            })
                        except:
                            pass
