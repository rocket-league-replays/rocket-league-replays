# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_profile_patreon_email_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='facebook_url',
            field=models.URLField(verbose_name=b'Facebook URL', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='reddit_username',
            field=models.CharField(verbose_name=b'reddit username', blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitch_username',
            field=models.CharField(verbose_name=b'Twitch.tv username', blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter_username',
            field=models.CharField(verbose_name=b'Twitter username', blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='youtube_url',
            field=models.URLField(verbose_name=b'YouTube URL', blank=True, null=True),
        ),
    ]
