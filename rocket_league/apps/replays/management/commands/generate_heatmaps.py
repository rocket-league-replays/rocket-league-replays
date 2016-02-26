import json
import os
import subprocess
import sys
from contextlib import contextmanager

from django.core.files import File
from django.core.management.base import BaseCommand
from django.db.models import Q

from ...models import Player, Replay


@contextmanager
def file_lock(lock_file):
    if os.path.exists(lock_file):
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
                Q(heatmap__isnull=True) | Q(heatmap=''),
            ).values_list('replay_id', flat=True)

            replays = Replay.objects.filter(
                id__in=players,
                processed=True,
            ).exclude(
                crashed_heatmap_parser=True,
            ).distinct()[:10]

            for replay in replays:
                # Does this replay have any players with heatmap files? If so,
                # the process probably crashed. So don't bother generating it
                # again.

                if replay.player_set.exclude(heatmap='').count() > 0:
                    replay.crashed_heatmap_parser = True
                    replay.save()
                    continue

                command = [
                    '/var/www/rocket-league-replays-heatmaps/.venv/bin/python',
                    '/var/www/rocket-league-replays-heatmaps/main.py',
                    replay.file.url
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
                        print 'Unable to get data for replay {}.'.format(replay.pk), e
                        data = []
                except subprocess.CalledProcessError as e:
                    # The parser crashed, not a lot we can do about this.. Just move on.
                    data = []
                    print 'CalledProcessError from replay {}'.format(replay.pk), e

                for player in data:
                    player_objs = replay.player_set.filter(
                        player_name=player,
                    )

                    tmp_file = open(data[player], 'rb')

                    for player_obj in player_objs:
                        tmp_file.seek(0)

                        # Don't re-save a heatmap, we'll just be filling up S3.
                        if player_obj.heatmap:
                            continue

                        player_obj.heatmap.save(
                            data[player].replace('/tmp/', ''),
                            File(tmp_file)
                        )
                        player_obj.save()

                    os.remove(data[player])
