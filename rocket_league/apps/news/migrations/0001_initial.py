# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import rocket_league.apps.news.models
import django.db.models.deletion
import cms.apps.media.models
from django.conf import settings
import django.utils.timezone
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_page_requires_authentication'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('media', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text=b"Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name=b'online')),
                ('browser_title', models.CharField(help_text=b"The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_keywords', models.CharField(help_text=b'A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.', max_length=1000, verbose_name=b'keywords', blank=True)),
                ('meta_description', models.TextField(help_text=b'A brief description of the contents of this page.', verbose_name=b'description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, b'Very high'), (0.8, b'High'), (0.5, b'Medium'), (0.3, b'Low'), (0.0, b'Very low')], blank=True, help_text=b'The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name=b'priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, b'Always'), (2, b'Hourly'), (3, b'Daily'), (4, b'Weekly'), (5, b'Monthly'), (6, b'Yearly'), (7, b'Never')], blank=True, help_text=b'How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name=b'change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name=b'allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name=b'follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name=b'allow archiving')),
                ('url_title', models.SlugField(verbose_name=b'URL title')),
                ('title', models.CharField(max_length=1000)),
                ('short_title', models.CharField(help_text=b'A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.', max_length=200, blank=True)),
                ('date', models.DateField(default=django.utils.timezone.now, db_index=True)),
                ('content', cms.models.fields.HtmlField(blank=True)),
                ('summary', cms.models.fields.HtmlField(blank=True)),
                ('status', models.CharField(default=b'draft', max_length=100, choices=[(b'draft', b'Draft'), (b'submitted', b'Submitted for approval'), (b'approved', b'Approved')])),
                ('authors', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'ordering': ('-date',),
                'permissions': (('can_approve_articles', 'Can approve articles'),),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text=b"Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name=b'online')),
                ('browser_title', models.CharField(help_text=b"The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_keywords', models.CharField(help_text=b'A comma-separated list of keywords for this page. Use this to specify common mis-spellings or alternative versions of important words in this page.', max_length=1000, verbose_name=b'keywords', blank=True)),
                ('meta_description', models.TextField(help_text=b'A brief description of the contents of this page.', verbose_name=b'description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, b'Very high'), (0.8, b'High'), (0.5, b'Medium'), (0.3, b'Low'), (0.0, b'Very low')], blank=True, help_text=b'The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name=b'priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, b'Always'), (2, b'Hourly'), (3, b'Daily'), (4, b'Weekly'), (5, b'Monthly'), (6, b'Yearly'), (7, b'Never')], blank=True, help_text=b'How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name=b'change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name=b'allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name=b'follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text=b'Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name=b'allow archiving')),
                ('url_title', models.SlugField(verbose_name=b'URL title')),
                ('title', models.CharField(max_length=1000)),
                ('short_title', models.CharField(help_text=b'A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.', max_length=200, blank=True)),
                ('content_primary', cms.models.fields.HtmlField(verbose_name=b'primary content', blank=True)),
            ],
            options={
                'ordering': ('title',),
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NewsFeed',
            fields=[
                ('page', models.OneToOneField(related_name='+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
                ('content_primary', cms.models.fields.HtmlField(verbose_name=b'primary content', blank=True)),
                ('per_page', models.IntegerField(default=5, null=True, verbose_name=b'articles per page', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set([('url_title',)]),
        ),
        migrations.AddField(
            model_name='article',
            name='categories',
            field=models.ManyToManyField(to='news.Category', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='article',
            name='news_feed',
            field=models.ForeignKey(default=rocket_league.apps.news.models.get_default_news_feed, to='news.NewsFeed'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='article',
            unique_together=set([('news_feed', 'date', 'url_title')]),
        ),
    ]
