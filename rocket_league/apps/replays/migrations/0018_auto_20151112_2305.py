# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0017_auto_20151104_1416'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='player_name',
            field=models.CharField(max_length=100, db_index=True),
        ),
    ]
