# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0009_player_user_entered'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='title',
            field=models.CharField(max_length=32, null=True, verbose_name=b'replay name', blank=True),
        ),
    ]
