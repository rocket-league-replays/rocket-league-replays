# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0043_auto_20160626_1930'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='player',
            unique_together=set([]),
        ),
    ]
