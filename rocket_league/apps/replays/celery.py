from __future__ import absolute_import

import os

from celery import Celery

if 'rocketleaguereplays.com' in os.uname()[1]:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rocket_league.settings.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rocket_league.settings.local')

from django.conf import settings  # noqa

app = Celery('rocket_league')

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
