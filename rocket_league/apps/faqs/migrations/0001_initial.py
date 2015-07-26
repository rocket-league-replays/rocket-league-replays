# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cms.apps.media.models
import django.db.models.deletion
import cms.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0005_social_fields'),
        ('media', '0002_auto_20150713_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text="Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name='online')),
                ('browser_title', models.CharField(help_text="The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_description', models.TextField(help_text='A brief description of the contents of this page.', verbose_name='description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, 'Very high'), (0.8, 'High'), (0.5, 'Medium'), (0.3, 'Low'), (0.0, 'Very low')], blank=True, help_text='The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name='priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, 'Always'), (2, 'Hourly'), (3, 'Daily'), (4, 'Weekly'), (5, 'Monthly'), (6, 'Yearly'), (7, 'Never')], blank=True, help_text='How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name='change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text='Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name='allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text='Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name='follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text='Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name='allow archiving')),
                ('og_title', models.CharField(help_text='Title that will appear on the Facebook post, it is limited to 100 charactersbecause Facebook truncates the title to 88 characters.', max_length=100, verbose_name='title', blank=True)),
                ('og_description', models.TextField(help_text='Description that will appear ont he Facebook post, it is limited to 300characters but is recommended not to use anything over 200.', max_length=300, verbose_name='description', blank=True)),
                ('twitter_card', models.IntegerField(default=None, choices=[(0, 'Summary'), (1, 'Photo'), (2, 'Video'), (3, 'Product'), (4, 'App'), (5, 'Gallery'), (6, 'Large Summary')], blank=True, help_text='The type of content on the page, most of the time summary will sufficeBefore you can benefit with any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved', null=True, verbose_name='card')),
                ('twitter_title', models.CharField(help_text='The title that appears on the Twitter card, it is limited to 70 characters.', max_length=70, verbose_name='title', blank=True)),
                ('twitter_description', models.TextField(help_text="Description that will appear on the Twitter card, it is limited to 200 charactersYou don't need to focus on keywords as this does'nt effect SEO so focus oncopy that compliments the tweet and title.", max_length=200, verbose_name='description', blank=True)),
                ('slug', models.SlugField(help_text='A user friendly URL')),
                ('title', models.CharField(max_length=1000)),
                ('short_title', models.CharField(help_text='A shorter version of the title that will be used in site navigation. Leave blank to use the full-length title.', max_length=200, blank=True)),
                ('content_primary', cms.models.fields.HtmlField(verbose_name=b'primary content', blank=True)),
                ('og_image', cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The recommended image size is 1200x627 (1.91/1 ratio) this gives you a bigstand out thumbnail. Using an image smaller than 400x209 will give you a verysmall thumbnail and splits your post into 2 columns.If you have text on the image make sure it is centered as Facebook crops imagesto get the text centered so you may lose some of your image.', null=True, verbose_name='image')),
                ('twitter_image', cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The minimum size it needs to be is 280x150, if you want to use a larger imagemake sure the card type is set to "Large Summary"', null=True, verbose_name='image')),
            ],
            options={
                'verbose_name': 'catgeory',
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Faq',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_online', models.BooleanField(default=True, help_text="Uncheck this box to remove the page from the public website. Logged-in admin users will still be able to view this page by clicking the 'view on site' button.", verbose_name='online')),
                ('browser_title', models.CharField(help_text="The heading to use in the user's web browser. Leave blank to use the page title. Search engines pay particular attention to this attribute.", max_length=1000, blank=True)),
                ('meta_description', models.TextField(help_text='A brief description of the contents of this page.', verbose_name='description', blank=True)),
                ('sitemap_priority', models.FloatField(default=None, choices=[(1.0, 'Very high'), (0.8, 'High'), (0.5, 'Medium'), (0.3, 'Low'), (0.0, 'Very low')], blank=True, help_text='The relative importance of this content in your site.  Search engines use this as a hint when ranking the pages within your site.', null=True, verbose_name='priority')),
                ('sitemap_changefreq', models.IntegerField(default=None, choices=[(1, 'Always'), (2, 'Hourly'), (3, 'Daily'), (4, 'Weekly'), (5, 'Monthly'), (6, 'Yearly'), (7, 'Never')], blank=True, help_text='How frequently you expect this content to be updated.Search engines use this as a hint when scanning your site for updates.', null=True, verbose_name='change frequency')),
                ('robots_index', models.BooleanField(default=True, help_text='Use this to prevent search engines from indexing this page. Disable this only if the page contains information which you do not wish to show up in search results.', verbose_name='allow indexing')),
                ('robots_follow', models.BooleanField(default=True, help_text='Use this to prevent search engines from following any links they find in this page. Disable this only if the page contains links to other sites that you do not wish to publicise.', verbose_name='follow links')),
                ('robots_archive', models.BooleanField(default=True, help_text='Use this to prevent search engines from archiving this page. Disable this only if the page is likely to change on a very regular basis. ', verbose_name='allow archiving')),
                ('og_title', models.CharField(help_text='Title that will appear on the Facebook post, it is limited to 100 charactersbecause Facebook truncates the title to 88 characters.', max_length=100, verbose_name='title', blank=True)),
                ('og_description', models.TextField(help_text='Description that will appear ont he Facebook post, it is limited to 300characters but is recommended not to use anything over 200.', max_length=300, verbose_name='description', blank=True)),
                ('twitter_card', models.IntegerField(default=None, choices=[(0, 'Summary'), (1, 'Photo'), (2, 'Video'), (3, 'Product'), (4, 'App'), (5, 'Gallery'), (6, 'Large Summary')], blank=True, help_text='The type of content on the page, most of the time summary will sufficeBefore you can benefit with any of these fields make sure to go to https://dev.twitter.com/docs/cards/validation/validator and get approved', null=True, verbose_name='card')),
                ('twitter_title', models.CharField(help_text='The title that appears on the Twitter card, it is limited to 70 characters.', max_length=70, verbose_name='title', blank=True)),
                ('twitter_description', models.TextField(help_text="Description that will appear on the Twitter card, it is limited to 200 charactersYou don't need to focus on keywords as this does'nt effect SEO so focus oncopy that compliments the tweet and title.", max_length=200, verbose_name='description', blank=True)),
                ('question', models.CharField(max_length=256)),
                ('answer', cms.models.fields.HtmlField()),
                ('url_title', models.CharField(unique=True, max_length=256)),
                ('order', models.PositiveIntegerField(default=0)),
                ('categories', models.ManyToManyField(to='faqs.Category', null=True, blank=True)),
                ('og_image', cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The recommended image size is 1200x627 (1.91/1 ratio) this gives you a bigstand out thumbnail. Using an image smaller than 400x209 will give you a verysmall thumbnail and splits your post into 2 columns.If you have text on the image make sure it is centered as Facebook crops imagesto get the text centered so you may lose some of your image.', null=True, verbose_name='image')),
            ],
            options={
                'ordering': ['order', 'id', 'question'],
                'verbose_name': 'faq',
                'verbose_name_plural': 'faqs',
            },
        ),
        migrations.CreateModel(
            name='Faqs',
            fields=[
                ('page', models.OneToOneField(related_name='+', primary_key=True, serialize=False, editable=False, to='pages.Page')),
                ('standfirst', models.TextField(null=True, blank=True)),
                ('per_page', models.IntegerField(default=5, null=True, verbose_name=b'faqs per page', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='faq',
            name='page',
            field=models.ForeignKey(to='faqs.Faqs'),
        ),
        migrations.AddField(
            model_name='faq',
            name='twitter_image',
            field=cms.apps.media.models.ImageRefField(related_name='+', on_delete=django.db.models.deletion.PROTECT, blank=True, to='media.File', help_text='The minimum size it needs to be is 280x150, if you want to use a larger imagemake sure the card type is set to "Large Summary"', null=True, verbose_name='image'),
        ),
    ]
