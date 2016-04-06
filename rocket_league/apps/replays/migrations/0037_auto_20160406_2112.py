# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0036_auto_20160403_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='boost_data',
            field=social.apps.django_app.default.fields.JSONField(blank=True, null=True, default='{}'),
        ),
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(blank=True, null=True, default=0, choices=[(3, 'UnrankedStandard'), (13, 'RankedStandard'), (12, 'RankedSoloStandard'), (10, 'RankedDuels'), (16, 'RocketLabs'), (4, 'UnrankedChaos'), (2, 'UnrankedDoubles'), (15, 'SnowDay'), (1, 'UnrankedDuels'), (11, 'RankedDoubles')]),
        ),
    ]
