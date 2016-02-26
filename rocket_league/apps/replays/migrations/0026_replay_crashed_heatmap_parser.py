# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0025_auto_20160210_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='crashed_heatmap_parser',
            field=models.BooleanField(default=False),
        ),
    ]
