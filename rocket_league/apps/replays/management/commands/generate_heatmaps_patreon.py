import os
import sys
import traceback
from contextlib import contextmanager

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ...models import Replay


@contextmanager
def file_lock(lock_file, options):
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

    def handle(self, *args, **options):
        num_processed = 0

        with file_lock('/tmp/generate_heatmaps_patreon.lock', options):
            # Get any replays which don't have a location JSON file. Check if
            # each replay is eligible to have one.

            if options['replay_id']:
                replays = Replay.objects.filter(pk=options['replay_id'])
            else:
                # Get any replays which don't have a location JSON file.
                replays_0 = Replay.objects.filter(
                    boostdata__isnull=True,
                ).exclude(
                    crashed_heatmap_parser=True
                ).order_by('-timestamp', '-average_rating')

                # Get any replays which don't have any boost data.
                replays_1 = Replay.objects.filter(
                    location_json_file__isnull=True,
                ).exclude(
                    crashed_heatmap_parser=True
                ).order_by('-timestamp', '-average_rating')

                replays = replays_0 | replays_1

            for replay in replays:
                # To avoid the queue getting too backlogged, only process a few
                # replays at a time.
                if num_processed >= 25:
                    return

                if replay.replay_id and replay.file:
                    needs_processing = False

                    if replay.eligble_for_feature('playback') and not replay.heatmap_json_file:
                        needs_processing = True

                    if replay.eligble_for_boost_analysis() and replay.boostdata_set.count() == 0:
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

                        if replay.eligble_for_playback() and not replay.heatmap_json_file:
                            replay_processed = False

                        if replay.eligble_for_boost_analysis() and replay.boostdata_set.count() == 0:
                            replay_processed = False

                        if not replay_processed:
                            replay.crashed_heatmap_parser = True
                            replay.save()
                        else:
                            num_processed += 1

                    except Exception:
                        replay.crashed_heatmap_parser = True
                        replay.save()

                        # https://opbeat.com/docs/articles/get-started-with-django/
                        print('Unable to process.')
                        traceback.print_exc()
