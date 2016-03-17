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
            name='facebook_url',
            field=models.URLField(blank=True, null=True, verbose_name=b'Facebook URL'),
        ),
        migrations.AddField(
            model_name='profile',
            name='patreon_email_address',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='patreon_level',
            field=models.DecimalField(max_digits=100, blank=True, default=0, null=True, decimal_places=2),
        ),
        migrations.AddField(
            model_name='profile',
            name='reddit_username',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'reddit username'),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitch_username',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Twitch.tv username'),
        ),
        migrations.AddField(
            model_name='profile',
            name='twitter_username',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name=b'Twitter username'),
        ),
        migrations.AddField(
            model_name='profile',
            name='youtube_url',
            field=models.URLField(blank=True, null=True, verbose_name=b'YouTube URL'),
        ),
    ]
