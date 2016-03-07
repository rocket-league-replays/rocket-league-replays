# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0029_auto_20160307_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='online_id',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(blank=True, null=True, default=0, choices=[(13, 'RankedStandard'), (4, 'UnrankedChaos'), (16, 'RocketLabs'), (11, 'RankedDoubles'), (12, 'RankedSoloStandard'), (10, 'RankedDuels'), (2, 'UnrankedDoubles'), (1, 'UnrankedDuels'), (3, 'UnrankedStandard')]),
        ),
    ]
