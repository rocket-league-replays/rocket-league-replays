# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0042_auto_20160515_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='replay',
            name='shot_data',
            field=social.apps.django_app.default.fields.JSONField(blank=True, null=True, default='{}'),
        ),
    ]
