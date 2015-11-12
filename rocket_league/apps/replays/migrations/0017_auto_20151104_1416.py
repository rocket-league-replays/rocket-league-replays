# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0016_auto_20151013_2245'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='online_id',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='platform',
            field=models.CharField(db_index=True, max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='replay',
            name='team_sizes',
            field=models.PositiveIntegerField(db_index=True, null=True, blank=True),
        ),
    ]
