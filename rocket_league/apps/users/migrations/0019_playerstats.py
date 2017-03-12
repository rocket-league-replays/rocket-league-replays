# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20160913_2030'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerStats',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('platform', models.CharField(max_length=100, db_index=True, blank=True, null=True)),
                ('online_id', models.CharField(max_length=128, db_index=True, blank=True, null=True)),
                ('wins', models.PositiveIntegerField(default=0)),
                ('assists', models.PositiveIntegerField(default=0)),
                ('goals', models.PositiveIntegerField(default=0)),
                ('shots', models.PositiveIntegerField(default=0)),
                ('mvps', models.PositiveIntegerField(default=0)),
                ('saves', models.PositiveIntegerField(default=0)),
            ],
        ),
    ]
