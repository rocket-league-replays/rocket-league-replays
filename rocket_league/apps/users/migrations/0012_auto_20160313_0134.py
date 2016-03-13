# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20160224_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='leaguerating',
            name='steamid',
            field=models.CharField(null=True, max_length=300, blank=True, db_index=True),
        ),
    ]
