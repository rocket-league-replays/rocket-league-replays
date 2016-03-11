# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0031_auto_20160307_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='spectator',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(choices=[(3, 'UnrankedStandard'), (12, 'RankedSoloStandard'), (1, 'UnrankedDuels'), (16, 'RocketLabs'), (11, 'RankedDoubles'), (4, 'UnrankedChaos'), (2, 'UnrankedDoubles'), (10, 'RankedDuels'), (13, 'RankedStandard')], default=0, blank=True, null=True),
        ),
    ]
