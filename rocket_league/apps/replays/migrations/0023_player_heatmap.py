# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0022_replay_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='heatmap',
            field=models.FileField(null=True, upload_to=b'uploads/heatmap_files', blank=True),
        ),
    ]
