# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rocket_league.apps.replays.models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0022_replay_season'),
        ('users', '0009_auto_20151104_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguerating',
            name='season',
            field=models.ForeignKey(default=rocket_league.apps.replays.models.get_default_season, to='replays.Season'),
        ),
    ]
