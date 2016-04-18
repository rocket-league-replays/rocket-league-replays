import os
import shutil
import sys
from contextlib import contextmanager

from django.core.files import File
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string

from ...models import ReplayPack


@contextmanager
def file_lock(lock_file):
    if os.path.exists(lock_file):
        print('Only one script can run at once. Script is locked with %s' % lock_file)
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
                print('Processing', obj.pk)
                zip_filename = '{}.zip'.format(obj.pk)
                tmp_folder = '/tmp/{}/'.format(obj.pk)
                zip_filepath = '/tmp/{}'.format(zip_filename)

                try:
                    shutil.rmtree(tmp_folder)
                except FileNotFoundError:
                    pass

                os.mkdir(tmp_folder)

                # Create a README file.
                with open('{}README.txt'.format(tmp_folder), 'w') as f:
                    readme = render_to_string('replays/readme.html', {
                        'replaypack': obj,
                    })

                    f.write(str(readme))

                for replay in obj.replays.all():
                    command = 'wget {} -qO {}{}.replay'.format(
                        replay.file.url,
                        tmp_folder,
                        replay.replay_id,
                    )

                    os.system(command)

                # Make the .zip
                command = 'rm {} 2> /dev/null; cd /tmp; zip -q ./{} ./{}/*'.format(
                    zip_filepath,
                    zip_filename,
                    obj.pk,
                )
                os.system(command)
                shutil.rmtree(tmp_folder)

                with open(zip_filepath, 'rb') as f:
                    zip_file = File(f)
                    obj.file.save(zip_filename, zip_file)

                os.remove(zip_filepath)
