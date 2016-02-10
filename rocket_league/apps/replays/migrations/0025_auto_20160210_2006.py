# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0024_auto_20160207_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='season',
            name='start_date',
            field=models.DateTimeField(),
        ),
    ]
