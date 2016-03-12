# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import cms.apps.media.models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0003_social_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='og_description',
            field=models.TextField(help_text='Description that will appear on Facebook posts. It is limited to 300 characters, but it is recommended that you do not use anything over 200.', max_length=300, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='og_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The recommended image size is 1200x627 (1.91:1 ratio); this gives you a big stand out thumbnail. Using an image smaller than 400x209 will give you a small thumbnail and will splits posts into 2 columns. If you have text on the image make sure it is centered.', null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='article',
            name='og_title',
            field=models.CharField(help_text='Title that will appear on Facebook posts. This is limited to 100 characters, but Facebook will truncate the title to 88 characters.', max_length=100, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='robots_archive',
            field=models.BooleanField(default=True, help_text='Uncheck this to prevent search engines from archiving this page. Do this this only if the page is likely to change on a very regular basis. ', verbose_name='allow archiving'),
        ),
        migrations.AlterField(
            model_name='article',
            name='robots_follow',
            field=models.BooleanField(default=True, help_text='Uncheck to prevent search engines from following any links they find in this page. Do this only if the page contains links to other sites that you do not wish to publicise.', verbose_name='follow links'),
        ),
        migrations.AlterField(
            model_name='article',
            name='robots_index',
            field=models.BooleanField(default=True, help_text='Uncheck to prevent search engines from indexing this page. Do this only if the page contains information which you do not wish to show up in search results.', verbose_name='allow indexing'),
        ),
        migrations.AlterField(
            model_name='article',
            name='sitemap_changefreq',
            field=models.IntegerField(default=None, choices=[(1, 'Always'), (2, 'Hourly'), (3, 'Daily'), (4, 'Weekly'), (5, 'Monthly'), (6, 'Yearly'), (7, 'Never')], blank=True, help_text='How frequently you expect this content to be updated. Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name='change frequency'),
        ),
        migrations.AlterField(
            model_name='article',
            name='sitemap_priority',
            field=models.FloatField(default=None, choices=[(1.0, 'Very high'), (0.8, 'High'), (0.5, 'Medium'), (0.3, 'Low'), (0.0, 'Very low')], blank=True, help_text='The relative importance of this content on your site. Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name='priority'),
        ),
        migrations.AlterField(
            model_name='article',
            name='twitter_card',
            field=models.IntegerField(default=None, choices=[(0, 'Summary'), (1, 'Photo'), (2, 'Video'), (3, 'Product'), (4, 'App'), (5, 'Gallery'), (6, 'Large Summary')], blank=True, help_text='The type of content on the page. Most of the time "Summary" will suffice. Before you can benefit from any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved.', null=True, verbose_name='card'),
        ),
        migrations.AlterField(
            model_name='article',
            name='twitter_description',
            field=models.TextField(help_text="Description that will appear on Twitter cards. It is limited to 200 characters. This does'nt effect SEO, so focus on copy that complements the tweet and title rather than on keywords.", max_length=200, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='article',
            name='twitter_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The minimum size it needs to be is 280x150. If you want to use a larger imagemake sure the card type is set to "Large Summary".', null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='category',
            name='og_description',
            field=models.TextField(help_text='Description that will appear on Facebook posts. It is limited to 300 characters, but it is recommended that you do not use anything over 200.', max_length=300, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='og_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The recommended image size is 1200x627 (1.91:1 ratio); this gives you a big stand out thumbnail. Using an image smaller than 400x209 will give you a small thumbnail and will splits posts into 2 columns. If you have text on the image make sure it is centered.', null=True, verbose_name='image'),
        ),
        migrations.AlterField(
            model_name='category',
            name='og_title',
            field=models.CharField(help_text='Title that will appear on Facebook posts. This is limited to 100 characters, but Facebook will truncate the title to 88 characters.', max_length=100, verbose_name='title', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='robots_archive',
            field=models.BooleanField(default=True, help_text='Uncheck this to prevent search engines from archiving this page. Do this this only if the page is likely to change on a very regular basis. ', verbose_name='allow archiving'),
        ),
        migrations.AlterField(
            model_name='category',
            name='robots_follow',
            field=models.BooleanField(default=True, help_text='Uncheck to prevent search engines from following any links they find in this page. Do this only if the page contains links to other sites that you do not wish to publicise.', verbose_name='follow links'),
        ),
        migrations.AlterField(
            model_name='category',
            name='robots_index',
            field=models.BooleanField(default=True, help_text='Uncheck to prevent search engines from indexing this page. Do this only if the page contains information which you do not wish to show up in search results.', verbose_name='allow indexing'),
        ),
        migrations.AlterField(
            model_name='category',
            name='sitemap_changefreq',
            field=models.IntegerField(default=None, choices=[(1, 'Always'), (2, 'Hourly'), (3, 'Daily'), (4, 'Weekly'), (5, 'Monthly'), (6, 'Yearly'), (7, 'Never')], blank=True, help_text='How frequently you expect this content to be updated. Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name='change frequency'),
        ),
        migrations.AlterField(
            model_name='category',
            name='sitemap_priority',
            field=models.FloatField(default=None, choices=[(1.0, 'Very high'), (0.8, 'High'), (0.5, 'Medium'), (0.3, 'Low'), (0.0, 'Very low')], blank=True, help_text='The relative importance of this content on your site. Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name='priority'),
        ),
        migrations.AlterField(
            model_name='category',
            name='twitter_card',
            field=models.IntegerField(default=None, choices=[(0, 'Summary'), (1, 'Photo'), (2, 'Video'), (3, 'Product'), (4, 'App'), (5, 'Gallery'), (6, 'Large Summary')], blank=True, help_text='The type of content on the page. Most of the time "Summary" will suffice. Before you can benefit from any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved.', null=True, verbose_name='card'),
        ),
        migrations.AlterField(
            model_name='category',
            name='twitter_description',
            field=models.TextField(help_text="Description that will appear on Twitter cards. It is limited to 200 characters. This does'nt effect SEO, so focus on copy that complements the tweet and title rather than on keywords.", max_length=200, verbose_name='description', blank=True),
        ),
        migrations.AlterField(
            model_name='category',
            name='twitter_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The minimum size it needs to be is 280x150. If you want to use a larger imagemake sure the card type is set to "Large Summary".', null=True, verbose_name='image'),
        ),
    ]
