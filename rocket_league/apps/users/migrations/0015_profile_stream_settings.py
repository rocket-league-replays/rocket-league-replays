# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0014_auto_20160320_0921'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='stream_settings',
            field=social.apps.django_app.default.fields.JSONField(default='{}', blank=True, null=True),
        ),
    ]
