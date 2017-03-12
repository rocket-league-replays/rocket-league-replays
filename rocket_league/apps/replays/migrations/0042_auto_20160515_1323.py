# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0041_auto_20160426_2125'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='privacy',
            field=models.PositiveIntegerField(choices=[(1, 'Private'), (2, 'Unlisted'), (3, 'Public')], default=3),
        )
    ]
