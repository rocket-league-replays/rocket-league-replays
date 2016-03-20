# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site', '0006_auto_20160319_2246'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='patron',
            name='patron_facebook',
        ),
        migrations.RemoveField(
            model_name='patron',
            name='patron_twitter',
        ),
        migrations.RemoveField(
            model_name='patron',
            name='patron_youtube',
        ),
    ]
