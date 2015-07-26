# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('site', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentcolumn',
            name='url',
            field=models.CharField(max_length=100, verbose_name=b'URL'),
        ),
    ]
