import os
import StringIO
import sys
from contextlib import contextmanager
from zipfile import ZipFile

import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ...models import ReplayPack


@contextmanager
def file_lock(lock_file):
    if os.path.exists(lock_file):
        print 'Only one script can run at once. '\
              'Script is locked with %s' % lock_file
        sys.exit(-1)
    else:
        open(lock_file, 'w').write("1")
        try:
            yield
        finally:
            os.remove(lock_file)


class Command(BaseCommand):
    help = "Generate ZIP files for replay packs without files"

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('replay_pack_id', nargs='?', type=int)

    def handle(self, *args, **options):
        with file_lock('/tmp/generate_replay_packs.lock'):
            if options['replay_pack_id']:
                replay_packs = ReplayPack.objects.filter(pk=options['replay_pack_id'])
            else:
                replay_packs = ReplayPack.objects.filter(
                    file='',
                )

            replay_packs = replay_packs.order_by('pk')

            for obj in replay_packs:
                print 'Processing', obj.pk
                zip_filename = '{}.zip'.format(str(obj))

                zip_string = StringIO.StringIO()

                with ZipFile(zip_string, 'w') as f:
                    for replay in obj.replays.all():
                        filename = '{}.replay'.format(replay.replay_id)

                        print 'Getting {}'.format(replay.file.url)
                        r = requests.get(replay.file.url, stream=True)

                        for chunk in r.iter_content(1024):
                            f.writestr(filename, chunk)

                    # Create a README file.
                    readme = render_to_string('replays/readme.html', {
                        'replaypack': obj,
                    })

                    f.writestr('README.txt', str(readme))
                f.close()

                obj.file.save(zip_filename, ContentFile(zip_string.getvalue()))
