# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0018_auto_20151112_2305'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='average_rating',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
    ]
