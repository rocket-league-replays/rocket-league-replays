# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0019_replay_average_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='average_rating',
            field=models.PositiveIntegerField(default=0, null=True, blank=True),
        ),
    ]
