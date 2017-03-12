# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0040_auto_20160421_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='replay',
            name='title',
            field=models.CharField(null=True, verbose_name='replay name', blank=True, max_length=64),
        ),
    ]
