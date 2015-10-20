# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_leaguerating_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='SteamCache',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=255)),
                ('extra_data', social.apps.django_app.default.fields.JSONField(default=b'{}')),
            ],
        ),
    ]
