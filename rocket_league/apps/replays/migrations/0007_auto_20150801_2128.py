# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('replays', '0006_auto_20150728_1257'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='replay',
            options={'ordering': ['-timestamp', '-pk']},
        ),
    ]
