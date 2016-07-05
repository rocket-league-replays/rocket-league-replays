import json
import sys
import traceback

import requests
from django.conf import settings
from django.utils.timezone import now
from io import StringIO

from .celery import app
from .models import Replay


@app.task
def report_to_slack(replay):
    print('[{}] Unable to process replay {}.'.format(now(), replay.pk))
    print('[{}] {}'.format(now(), traceback.format_exc()))

    requests.post(settings.SLACK_URL, data={
        'payload': json.dumps({
            'channel': '#cronjobs',
            'username': 'Cronjob Bot',
            'icon_emoji': ':timer_clock:',
            'text': '[{}] Unable to process replay {}.```{}```'.format(
                now(),
                replay.pk,
                traceback.format_exc()
            )
        })
    })


@app.task(bind=True, name='rocket_league.apps.replays.tasks.process_netstream', ignore_result=False, track_started=True)
def process_netstream(self, replay_pk):
    prev_stdout, prev_stderr, sys.stdout, sys.stderr = sys.stdout, sys.stderr, StringIO(), StringIO()

    try:
        replay = Replay.objects.get(pk=replay_pk)

        try:
            replay.processed = False
            replay.crashed_heatmap_parser = False
            replay.save(parse_netstream=True)

            replay = Replay.objects.get(pk=replay_pk)

            replay_processed = True

            if not replay.location_json_file:
                replay_processed = False

            if replay.boostdata_set.count() == 0:
                replay_processed = False

            if not replay_processed:
                replay.crashed_heatmap_parser = True
                replay.save()

                self.update_state(state='FAILURE', meta={
                    'stdout': sys.stdout.getvalue(),
                    'stderr': sys.stderr.getvalue()
                })

        except Exception:
            replay = Replay.objects.get(pk=replay_pk)
            replay.crashed_heatmap_parser = True
            replay.save()

            self.update_state(state='FAILURE', meta={
                'stdout': sys.stdout.getvalue(),
                'stderr': sys.stderr.getvalue()
            })

    finally:
        sys.stdout = prev_stdout
        sys.stderr = prev_stderr
