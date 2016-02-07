import json
import os
import subprocess
import sys
from contextlib import contextmanager

from django.core.files import File
from django.core.management.base import BaseCommand

from ...models import Player, Replay


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
    help = "Generate heatmaps for replays."

    def handle(self, *args, **options):
        # cpulimit -l 50 /var/www/rocket-league-replays-heatmaps/.venv/bin/python /var/www/rocket-league-replays-heatmaps/main.py /var/www/rocket_league_media/uploads/replay_files/0AB522614886E7013F47349B85FAF720.replay 2> /dev/null

        with file_lock('/tmp/generate_heatmaps.lock'):
            players = Player.objects.filter(
                heatmap__isnull=True,
            ).values_list('replay_id', flat=True)

            replays = Replay.objects.filter(
                id__in=players,
            ).distinct()

            for replay in replays:
                print 'Replay', replay.pk
                command = [
                    'cpulimit',
                    '-l',
                    '90',
                    '/var/www/rocket-league-replays-heatmaps/.venv/bin/python',
                    '/var/www/rocket-league-replays-heatmaps/main.py',
                    replay.file.path
                ]

                try:
                    process = subprocess.check_output(command)
                    data = json.loads(process)
                except OSError:
                    # Try to run it in a development environment.
                    try:
                        command = [
                            '/Users/danielsamuels/Workspace/personal/rocket-league-replays-heatmaps/.venv/bin/python',
                            '/Users/danielsamuels/Workspace/personal/rocket-league-replays-heatmaps/main.py',
                            replay.file.path
                        ]

                        process = subprocess.check_output(command)
                        data = json.loads(process)
                    except Exception as e:
                        print 'Unable to get data.', e
                        data = []

                for player in data:
                    player_objs = replay.player_set.filter(
                        player_name=player,
                    )

                    tmp_file = open(data[player], 'rb')

                    for player_obj in player_objs:
                        tmp_file.seek(0)

                        player_obj.heatmap.save(
                            data[player].replace('/tmp/', ''),
                            File(tmp_file)
                        )
                        player_obj.save()
