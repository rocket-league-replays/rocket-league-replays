# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0030_auto_20160307_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(choices=[(12, 'RankedSoloStandard'), (2, 'UnrankedDoubles'), (11, 'RankedDoubles'), (4, 'UnrankedChaos'), (13, 'RankedStandard'), (16, 'RocketLabs'), (10, 'RankedDuels'), (3, 'UnrankedStandard'), (1, 'UnrankedDuels')], null=True, blank=True, default=0),
        ),
        migrations.AlterUniqueTogether(
            name='player',
            unique_together=set([('unique_id', 'replay')]),
        ),
    ]
