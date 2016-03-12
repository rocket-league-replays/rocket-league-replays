# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0026_replay_crashed_heatmap_parser'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(default=0, null=True, blank=True, choices=[(1, 'UnrankedDuels'), (4, 'UnrankedChaos'), (12, 'RankedSoloStandard'), (3, 'UnrankedStandard'), (2, 'UnrankedDoubles'), (13, 'RankedStandard'), (10, 'RankedDuels'), (11, 'RankedDoubles')]),
        ),
        migrations.AlterField(
            model_name='map',
            name='image',
            field=models.FileField(null=True, blank=True, upload_to='uploads/files'),
        ),
        migrations.AlterField(
            model_name='player',
            name='heatmap',
            field=models.FileField(null=True, blank=True, upload_to='uploads/heatmap_files'),
        ),
        migrations.AlterField(
            model_name='replay',
            name='file',
            field=models.FileField(upload_to='uploads/replay_files'),
        ),
        migrations.AlterField(
            model_name='replay',
            name='max_replay_size_mb',
            field=models.IntegerField(default=10, null=True, blank=True, verbose_name='max replay size (MB)'),
        ),
        migrations.AlterField(
            model_name='replay',
            name='record_fps',
            field=models.FloatField(default=30.0, null=True, blank=True, verbose_name='record FPS'),
        ),
        migrations.AlterField(
            model_name='replay',
            name='replay_id',
            field=models.CharField(null=True, max_length=100, blank=True, verbose_name='replay ID'),
        ),
        migrations.AlterField(
            model_name='replay',
            name='title',
            field=models.CharField(null=True, max_length=32, blank=True, verbose_name='replay name'),
        ),
        migrations.AlterField(
            model_name='replaypack',
            name='file',
            field=models.FileField(null=True, blank=True, upload_to='uploads/replaypack_files'),
        ),
    ]
