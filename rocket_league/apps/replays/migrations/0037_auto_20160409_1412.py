# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0036_auto_20160409_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='date_created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
