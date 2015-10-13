# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0013_replaypack_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='assists',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='bot',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='player',
            name='goals',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='online_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='platform',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='saves',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='score',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='player',
            name='shots',
            field=models.PositiveIntegerField(default=0, blank=True),
        ),
    ]
