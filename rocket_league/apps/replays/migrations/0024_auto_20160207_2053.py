# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0023_player_heatmap'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='team_0_score',
            field=models.IntegerField(default=0, null=True, db_index=True, blank=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='team_1_score',
            field=models.IntegerField(default=0, null=True, db_index=True, blank=True),
        ),
    ]
