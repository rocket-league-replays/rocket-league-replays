# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0032_auto_20160311_2039'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ('team', '-score', 'player_name')},
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(choices=[(3, 'UnrankedStandard'), (11, 'RankedDoubles'), (13, 'RankedStandard'), (12, 'RankedSoloStandard'), (1, 'UnrankedDuels'), (10, 'RankedDuels'), (4, 'UnrankedChaos'), (16, 'RocketLabs'), (2, 'UnrankedDoubles')], blank=True, null=True, default=0),
        ),
    ]
