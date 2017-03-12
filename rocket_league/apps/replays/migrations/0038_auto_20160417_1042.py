# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0037_auto_20160409_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='vehicle_loadout',
            field=social.apps.django_app.default.fields.JSONField(default='{}', blank=True, null=True),
        ),
    ]
