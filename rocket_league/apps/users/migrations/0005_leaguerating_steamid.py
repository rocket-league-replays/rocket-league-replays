# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_leaguerating_standard'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguerating',
            name='steamid',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
