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
        migrations.AlterField(
            model_name='replay',
            name='playlist',
            field=models.PositiveIntegerField(null=True, default=0, blank=True, choices=[(13, 'RankedStandard'), (16, 'RocketLabs'), (11, 'RankedDoubles'), (4, 'UnrankedChaos'), (10, 'RankedDuels'), (12, 'RankedSoloStandard'), (2, 'UnrankedDoubles'), (3, 'UnrankedStandard'), (15, 'SnowDay'), (1, 'UnrankedDuels')]),
        ),
        migrations.AddField(
            model_name='boostdata',
            name='replay',
            field=models.ForeignKey(to='replays.Replay'),
        ),
    ]
