
import traceback
from django.core.management.base import BaseCommand

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
            replays = Replay.objects.all()

        replays = replays.filter(
            location_json_file__isnull=True,
        ).exclude(
            crashed_heatmap_parser=True,
        )

        replays = replays.order_by('-pk')[:10]

        for replay in replays:
            if replay.replay_id and replay.file:
                print('Processing', replay.pk, '-', replay.replay_id)

                try:
                    replay.processed = False
                    replay.save(parse_netstream=True)
                except Exception:
                    replay.crashed_heatmap_parser = True
                    replay.save()

                    print('Unable to process.')
                    traceback.print_exc()
