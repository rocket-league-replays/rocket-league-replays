# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0028_auto_20160307_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='location_json_file',
            field=models.FileField(upload_to='uploads/replay_json_files', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(default=0, choices=[(2, 'UnrankedDoubles'), (10, 'RankedDuels'), (11, 'RankedDoubles'), (12, 'RankedSoloStandard'), (13, 'RankedStandard'), (1, 'UnrankedDuels'), (4, 'UnrankedChaos'), (3, 'UnrankedStandard')], blank=True, null=True),
        ),
    ]
