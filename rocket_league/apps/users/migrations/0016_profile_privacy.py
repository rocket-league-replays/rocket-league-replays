# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0015_profile_stream_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='privacy',
            field=models.PositiveIntegerField(default=3, choices=[(1, 'Private'), (2, 'Unlisted'), (3, 'Public')]),
        ),
    ]
