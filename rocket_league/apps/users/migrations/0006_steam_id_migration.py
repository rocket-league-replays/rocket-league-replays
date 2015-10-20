# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def migrate_steam_ids(apps, schema_editor):
    LeagueRating = apps.get_model('users', 'LeagueRating')

    for rating in LeagueRating.objects.all():
        # Get the Steam ID for this user.
        rating.steamid = rating.user.social_auth.get(
            provider='steam',
        ).uid
        rating.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_leaguerating_steamid'),
    ]

    operations = [
        migrations.RunPython(migrate_steam_ids),
    ]
