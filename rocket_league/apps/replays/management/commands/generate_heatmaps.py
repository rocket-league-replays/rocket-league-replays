import os
import sys
import traceback
from contextlib import contextmanager

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from ...models import Replay


@contextmanager
def file_lock(lock_file):
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
        with file_lock('/tmp/generate_heatmaps.lock'):
            if options['replay_id']:
                replays = Replay.objects.filter(pk=options['replay_id'])
            else:
                replays = Replay.objects.all()

            replays = replays.filter(
                location_json_file='',
            ).exclude(
                crashed_heatmap_parser=True,
            )

            replays = replays.order_by('-pk')[:10]

            for replay in replays:
                if replay.replay_id and replay.file:
                    print('[{}] Processing {} - {}'.format(
                        now(),
                        replay.pk,
                        replay.replay_id
                    ))

                    try:
                        replay.processed = False
                        replay.save(parse_netstream=True)
                    except Exception:
                        replay.crashed_heatmap_parser = True
                        replay.save()

                        print('Unable to process.')
                        traceback.print_exc()
