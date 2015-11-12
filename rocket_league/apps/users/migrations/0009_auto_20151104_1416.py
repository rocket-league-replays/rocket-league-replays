# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_steamcache'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguerating',
            name='steamid',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='steamcache',
            name='uid',
            field=models.CharField(max_length=255, db_index=True),
        ),
    ]
