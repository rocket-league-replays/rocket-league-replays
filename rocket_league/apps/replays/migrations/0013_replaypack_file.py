# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0012_replay_excitement_factor'),
    ]

    operations = [
        migrations.AddField(
            model_name='replaypack',
            name='file',
            field=models.FileField(null=True, upload_to=b'uploads/replaypack_files', blank=True),
        ),
    ]
