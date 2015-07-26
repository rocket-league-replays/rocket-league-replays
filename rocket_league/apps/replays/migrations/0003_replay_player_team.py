# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0002_auto_20150726_1623'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='player_team',
            field=models.IntegerField(default=0),
        ),
    ]
