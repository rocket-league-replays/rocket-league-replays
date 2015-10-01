# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_leaguerating'),
    ]

    operations = [
        migrations.RenameField(
            model_name='leaguerating',
            old_name='standard',
            new_name='solo_standard',
        ),
    ]
