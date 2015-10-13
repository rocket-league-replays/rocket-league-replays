# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0015_replay_show_leaderboard'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='player',
            options={'ordering': ('team', '-score')},
        ),
    ]
