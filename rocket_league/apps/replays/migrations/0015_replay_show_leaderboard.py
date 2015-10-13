# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0014_auto_20151013_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='show_leaderboard',
            field=models.BooleanField(default=False),
        ),
    ]
