from datetime import timedelta

from cms import externals
from cms.apps.pages.models import Page
from cms.models import publication_manager
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.utils.timezone import now

from ..models import (Article, Category, CategoryHistoryLinkAdapter, NewsFeed,
                      get_default_news_feed, get_default_news_page)


class TestNews(TestCase):

    def _create_objects(self):
        with externals.watson.context_manager("update_index")():
            self.date = now()
            self.date_str = '/{}/{}/{}'.format(
                self.date.strftime('%Y'),
                self.date.strftime('%b').lower(),
                self.date.strftime('%d').lstrip('0'),
            )

            content_type = ContentType.objects.get_for_model(NewsFeed)

            self.page = Page.objects.create(
                title="News Feed",
                content_type=content_type,
            )

            self.feed = NewsFeed.objects.create(
                page=self.page,
            )

            self.category = Category.objects.create(
                slug='foo'
            )

            self.article = Article.objects.create(
                news_feed=self.feed,
                title='Foo',
                slug='foo',
                date=self.date,
            )
            self.article.categories.add(self.category)

            self.article_2 = Article.objects.create(
                news_feed=self.feed,
                title='Foo 2',
                slug='foo2',
                date=self.date + timedelta(days=10)
            )

            self.article_3 = Article.objects.create(
                news_feed=self.feed,
                title='Foo 3',
                slug='foo3',
                status='approved',
                date=self.date,
            )

    def test_get_default_news_page_no_pages(self):
        self.assertIsNone(get_default_news_page())

    def test_get_default_news_page_with_pages(self):
        self._create_objects()
        self.assertEqual(get_default_news_page(), self.page)

    def test_get_default_news_feed_no_pages(self):
        self.assertIsNone(get_default_news_feed())

    def test_get_default_news_feed_with_pages(self):
        self._create_objects()
        self.assertEqual(get_default_news_feed(), self.feed)

    def test_category_get_permalink_for_page(self):
        self._create_objects()
        self.assertEqual(self.category._get_permalink_for_page(self.page), '/foo/')

    def test_category_get_permalinks(self):
        self._create_objects()
        self.assertEqual(self.category._get_permalinks(), {'page_' + str(self.page.pk): '/foo/'})

    def test_categoryhistorylinkadapter_get_permalinks(self):
        self._create_objects()
        adapter = CategoryHistoryLinkAdapter()
        self.assertEqual(adapter.get_permalinks(self.category), {'page_' + str(self.page.pk): '/foo/'})

    def test_article_get_permalink_for_page(self):
        self._create_objects()
        self.assertEqual(self.article._get_permalink_for_page(self.page), self.date_str + '/foo/')

    def test_article_get_absolute_url(self):
        self._create_objects()
        self.assertEqual(self.article.get_absolute_url(), self.date_str + '/foo/')

    def test_articlemanager_select_published(self):
        self._create_objects()

        with publication_manager.select_published(True):
            self.assertEqual(Article.objects.count(), 2)

        with publication_manager.select_published(False):
            self.assertEqual(Article.objects.count(), 3)

        # We have to manually enable the publication manager as middleware
        # isn't run during tests.
        with publication_manager.select_published(True):
            with self.settings(NEWS_APPROVAL_SYSTEM=True):
                self.assertEqual(Article.objects.count(), 1)
                self.assertEqual(len(Article.objects.all()), 1)

        # We need to generate an exception within the published block.
        with self.assertRaises(TypeError), \
                publication_manager.select_published(True):
            assert 1 / 'a'
