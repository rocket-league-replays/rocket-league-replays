# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_leaguerating_season'),
    ]

    operations = [
        migrations.AddField(
            model_name='leaguerating',
            name='doubles_division',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='doubles_matches_played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='doubles_mmr',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='duels_division',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='duels_matches_played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='duels_mmr',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='solo_standard_division',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='solo_standard_matches_played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='solo_standard_mmr',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='standard_division',
            field=models.IntegerField(default=-1),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='standard_matches_played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='standard_mmr',
            field=models.FloatField(default=0),
        ),
    ]
