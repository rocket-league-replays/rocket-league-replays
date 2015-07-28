# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0005_auto_20150727_2025'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goal',
            options={'ordering': ['number']},
        ),
        migrations.AddField(
            model_name='goal',
            name='frame',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='replay',
            name='keyframe_delay',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='replay',
            name='max_channels',
            field=models.IntegerField(default=1023, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='replay',
            name='max_replay_size_mb',
            field=models.IntegerField(default=10, null=True, verbose_name=b'max replay size (MB)', blank=True),
        ),
        migrations.AddField(
            model_name='replay',
            name='num_frames',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='replay',
            name='record_fps',
            field=models.FloatField(default=30.0, null=True, verbose_name=b'record FPS', blank=True),
        ),
    ]
