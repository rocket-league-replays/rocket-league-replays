# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0003_replay_player_team'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='player_team',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
    ]
