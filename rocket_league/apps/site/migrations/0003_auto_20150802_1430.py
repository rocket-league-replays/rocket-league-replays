# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_social_fields'),
        ('site', '0002_auto_20150726_1813'),
    ]

    operations = [
        migrations.CreateModel(
            name='Placeholder',
            fields=[
                ('page', models.OneToOneField(related_name='+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='content',
            options={'verbose_name': 'homepage'},
        ),
    ]
