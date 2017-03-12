# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0017_auto_20160911_2126'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='leaguerating',
            unique_together=set([('platform', 'online_id', 'playlist')]),
        ),
    ]
