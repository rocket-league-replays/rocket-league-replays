    # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0004_auto_20151002_1655'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='news_feed',
            field=models.ForeignKey(to='news.NewsFeed', null=True),
        ),
    ]
