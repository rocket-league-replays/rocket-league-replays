# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='url_title',
            new_name='slug',
        ),
        migrations.RenameField(
            model_name='category',
            old_name='url_title',
            new_name='slug',
        ),
    ]
