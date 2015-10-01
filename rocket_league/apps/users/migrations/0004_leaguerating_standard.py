# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20151001_2201'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguerating',
            name='standard',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
