import json
import traceback

import requests
from django.conf import settings
from django.utils.timezone import now

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


@app.task(name='rocket_league.apps.replays.tasks.process_netstream', ignore_result=False, track_started=True)
def process_netstream(replay_pk):
    replay = Replay.objects.get(pk=replay_pk)

    try:
        replay.processed = False
        replay.crashed_heatmap_parser = False
        replay.save(parse_netstream=True)

        replay.refresh_from_db()

        replay_processed = True

        if not replay.location_json_file:
            replay_processed = False

        if replay.boostdata_set.count() == 0:
            replay_processed = False

        if not replay_processed:
            replay.crashed_heatmap_parser = True
            replay.save()

            report_to_slack.apply_async([replay])

    except Exception:
        replay.refresh_from_db()
        replay.crashed_heatmap_parser = True
        replay.save()

        report_to_slack.apply_async([replay])
