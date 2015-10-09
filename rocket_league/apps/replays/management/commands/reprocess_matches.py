from django.core.management.base import BaseCommand

from ...models import Replay


class Command(BaseCommand):
    help = "Re-process all replays."

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('replay_id', nargs='?', type=int)

    def handle(self, *args, **options):
        if options['replay_id']:
            replays = Replay.objects.filter(pk=options['replay_id'])
        else:
            replays = Replay.objects.all()

        for replay in replays:
            if replay.replay_id and replay.file:
                print 'Processing', replay.pk, '-', replay.replay_id

                try:
                    replay.processed = False
                    replay.save()
                except Exception:
                    print 'Unable to process.'
