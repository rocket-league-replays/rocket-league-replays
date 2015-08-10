# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0011_replaypack'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='excitement_factor',
            field=models.FloatField(default=0.0),
        ),
    ]
