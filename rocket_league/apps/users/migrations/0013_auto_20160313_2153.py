# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.apps.django_app.default.fields


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20160313_0134'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='facebook_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='patreon_email_address',
            field=models.EmailField(max_length=254, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='patreon_level',
            field=models.DecimalField(null=True, decimal_places=2, blank=True, max_digits=100),
        ),
        migrations.AddField(
            model_name='profile',
            name='reddit_username',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitch_username',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter_username',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='youtube_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
