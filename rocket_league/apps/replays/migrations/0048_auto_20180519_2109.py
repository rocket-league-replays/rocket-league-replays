# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0047_auto_20170208_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='match_type',
            field=models.CharField(max_length=16, blank=True, null=True),
        ),
    ]
