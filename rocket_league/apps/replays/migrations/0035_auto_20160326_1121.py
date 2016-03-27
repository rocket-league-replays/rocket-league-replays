# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0034_auto_20160326_1117'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='location_json_file',
            field=models.FileField(blank=True, upload_to='uploads/replay_location_json_files', null=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(blank=True, default=0, choices=[(1, 'UnrankedDuels'), (10, 'RankedDuels'), (16, 'RocketLabs'), (2, 'UnrankedDoubles'), (12, 'RankedSoloStandard'), (11, 'RankedDoubles'), (3, 'UnrankedStandard'), (13, 'RankedStandard'), (4, 'UnrankedChaos'), (15, 'SnowDay')], null=True),
        ),
    ]
