# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('faqs', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='og_image',
        ),
        migrations.RemoveField(
            model_name='category',
            name='twitter_image',
        ),
        migrations.RemoveField(
            model_name='faq',
            name='categories',
        ),
        migrations.DeleteModel(
            name='Category',
        ),
    ]
