# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0035_auto_20160326_1121'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoostData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('frame', models.PositiveIntegerField()),
                ('value', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(255)])),
                ('player', models.ForeignKey(to='replays.Player')),
            ],
            options={
                'ordering': ['player', 'frame'],
            },
        ),
    ]
