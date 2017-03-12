# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0038_auto_20160417_1042'),
    ]

    operations = [
        migrations.CreateModel(
            name='Body',
            fields=[
                ('id', models.PositiveIntegerField(serialize=False, primary_key=True, db_index=True, unique=True)),
                ('name', models.CharField(max_length=100, default='Unknown')),
            ],
        ),
    ]
