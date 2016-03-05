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
            field=models.PositiveIntegerField(choices=[(2, 'UnrankedDoubles'), (3, 'UnrankedStandard'), (12, 'RankedSoloStandard'), (1, 'UnrankedDuels'), (10, 'RankedDuels'), (11, 'RankedDoubles'), (13, 'RankedStandard'), (4, 'UnrankedChaos')], default=0),
        )
    ]
