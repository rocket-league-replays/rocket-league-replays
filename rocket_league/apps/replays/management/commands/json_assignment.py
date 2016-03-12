import traceback
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage

from ...models import Replay


class Command(BaseCommand):
    help = "Generate location JSON files for replays which are missing it."

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('replay_id', nargs='?', type=int)

    def handle(self, *args, **options):
        if options['replay_id']:
            replays = Replay.objects.filter(pk=options['replay_id'])
        else:
            replays = Replay.objects.filter(
                location_json_file__isnull=True,
            ).exclude(
                crashed_heatmap_parser=True,
            ).order_by('-pk')

        for replay in replays:
            # Attempt to assign the JSON file, if it doesn't exist it'll throw
            # an error, if it does, then great!
            print('Processing', replay.pk, '-', replay.replay_id)

            file_name = 'uploads/replay_json_files/{}.json'.format(
                replay.replay_id,
            )

            if default_storage.exists(file_name):
                replay.location_json_file = file_name
                replay.save()

        # Ensure replays have JSON files that actually exist.
        print('=== STAGE 2 ===')
        replays = Replay.objects.exclude(
            location_json_file__isnull=True,
        ).order_by('-pk')

        for replay in replays:
            if not replay.location_json_file:
                continue

            print('Processing', replay.pk, '-', replay.replay_id)
            if not default_storage.exists(replay.location_json_file):
                replay.location_json_file = None
                replay.save()
