# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_profile_privacy'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='leaguerating',
            name='doubles',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='doubles_division',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='doubles_matches_played',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='doubles_mmr',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='duels',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='duels_division',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='duels_matches_played',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='duels_mmr',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='season',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='solo_standard',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='solo_standard_division',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='solo_standard_matches_played',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='solo_standard_mmr',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='standard',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='standard_division',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='standard_matches_played',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='standard_mmr',
        ),
        migrations.RemoveField(
            model_name='leaguerating',
            name='steamid',
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='division',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Division I'), (1, 'Division II'), (2, 'Division III'), (3, 'Division IV'), (4, 'Division V')]),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='matches_played',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='online_id',
            field=models.CharField(max_length=128, blank=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='platform',
            field=models.CharField(max_length=100, blank=True, null=True, db_index=True),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='playlist',
            field=models.PositiveIntegerField(default=0, choices=[(6, b'Hoops'), (11, b'RankedDoubles'), (10, b'RankedDuels'), (12, b'RankedSoloStandard'), (13, b'RankedStandard'), (16, b'RocketLabs'), (15, b'SnowDay'), (4, b'UnrankedChaos'), (2, b'UnrankedDoubles'), (1, b'UnrankedDuels'), (3, b'UnrankedStandard')]),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='skill',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='tier',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Unranked'), (1, 'Prospect I'), (2, 'Prospect II'), (3, 'Prospect III'), (4, 'Prospect Elite'), (5, 'Challenger I'), (6, 'Challenger II'), (7, 'Challenger III'), (8, 'Challenger Elite'), (9, 'Rising Star'), (10, 'Shooting Star'), (11, 'All-Star'), (12, 'Superstar'), (13, 'Champion'), (14, 'Super Champion'), (15, 'Grand Champion')]),
        ),
        migrations.AddField(
            model_name='leaguerating',
            name='tier_max',
            field=models.PositiveIntegerField(default=0, choices=[(0, 'Unranked'), (1, 'Prospect I'), (2, 'Prospect II'), (3, 'Prospect III'), (4, 'Prospect Elite'), (5, 'Challenger I'), (6, 'Challenger II'), (7, 'Challenger III'), (8, 'Challenger Elite'), (9, 'Rising Star'), (10, 'Shooting Star'), (11, 'All-Star'), (12, 'Superstar'), (13, 'Champion'), (14, 'Super Champion'), (15, 'Grand Champion')]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='privacy',
            field=models.PositiveIntegerField(default=3, verbose_name='replay privacy', choices=[(1, b'Private'), (2, b'Unlisted'), (3, b'Public')]),
        ),
    ]
