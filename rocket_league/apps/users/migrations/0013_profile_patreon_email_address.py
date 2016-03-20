# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20160313_0134'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='patreon_email_address',
            field=models.EmailField(null=True, unique=True, blank=True, max_length=254),
        ),
    ]
