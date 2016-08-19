# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0045_auto_20160710_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='title',
            field=models.CharField(verbose_name='replay name', null=True, blank=True, max_length=128),
        ),
    ]
