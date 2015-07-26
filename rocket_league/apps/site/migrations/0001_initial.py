# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_social_fields'),
        ('media', '0002_auto_20150713_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('page', models.OneToOneField(related_name='+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContentColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('url', models.URLField(verbose_name=b'URL')),
                ('image', cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, to='media.File')),
                ('page', models.ForeignKey(to='pages.Page')),
            ],
        ),
    ]
