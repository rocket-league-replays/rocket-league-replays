# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0039_auto_20160417_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='replay_id',
            field=models.CharField(db_index=True, null=True, max_length=100, blank=True, verbose_name='replay ID'),
        ),
    ]
