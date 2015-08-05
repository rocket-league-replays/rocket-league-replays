# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_social_fields'),
        ('site', '0003_auto_20150802_1430'),
    ]

    operations = [
        migrations.CreateModel(
            name='StandardPage',
            fields=[
                ('page', models.OneToOneField(related_name='+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
                ('content_primary', cms.models.fields.HtmlField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
