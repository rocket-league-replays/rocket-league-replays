# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0033_auto_20160312_1130'),
    ]

    operations = [
        migrations.RenameField(
            model_name='replay',
            old_name='location_json_file',
            new_name='heatmap_json_file',
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(choices=[(2, 'UnrankedDoubles'), (4, 'UnrankedChaos'), (1, 'UnrankedDuels'), (13, 'RankedStandard'), (15, 'SnowDay'), (16, 'RocketLabs'), (11, 'RankedDoubles'), (3, 'UnrankedStandard'), (10, 'RankedDuels'), (12, 'RankedSoloStandard')], null=True, default=0, blank=True),
        ),
    ]
