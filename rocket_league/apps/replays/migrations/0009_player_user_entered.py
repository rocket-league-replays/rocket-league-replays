# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0008_auto_20150806_0801'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='user_entered',
            field=models.BooleanField(default=False),
        ),
    ]
