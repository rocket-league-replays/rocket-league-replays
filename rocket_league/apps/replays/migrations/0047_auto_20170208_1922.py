# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0046_auto_20160819_0947'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='goal',
            options={'ordering': ['frame']},
        ),
        migrations.AlterField(
            model_name='player',
            name='total_xp',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
