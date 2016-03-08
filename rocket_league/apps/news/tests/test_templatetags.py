from cms import externals
from cms.apps.pages.models import ContentBase, Page
from django.contrib.contenttypes.models import ContentType
from django.template import VariableDoesNotExist
from django.test import TestCase
from django.utils.timezone import now

from ..models import Article, Category, NewsFeed
from ..templatetags.news import (article_archive_url, article_date_list,
                                 article_day_archive_url, article_url,
                                 article_year_archive_url, category_url,
                                 get_page_from_context, page_context,
                                 takes_article_page, takes_current_page)


class TestPageContent(ContentBase):
    pass


class Object(object):
    pass


class NewsTest(TestCase):

    def setUp(self):
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(TestPageContent)

            self.homepage = Page.objects.create(
                title="Homepage",
                slug='homepage',
                content_type=content_type,
            )

            TestPageContent.objects.create(
                page=self.homepage,
            )

    def _create_feed_article(self):
        self.date = now()
        self.date_str = '/{}/{}/{}'.format(
            self.date.strftime('%Y'),
            self.date.strftime('%b').lower(),
            self.date.strftime('%d').lstrip('0'),
        )

        # Create a NewsFeed page.
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(NewsFeed)

            self.page = Page.objects.create(
                title="News Feed",
                slug='news',
                parent=self.homepage,
                content_type=content_type,
            )

            self.feed = NewsFeed.objects.create(
                page=self.page,
            )

            self.category = Category.objects.create(
                slug='foo'
            )

        # Create an Article.
        self.article = Article.objects.create(
            news_feed=self.feed,
            title='Article',
            slug='foo',
            date=self.date,
        )

    def test_page_context(self):
        def inner_function(context):
            return context

        initial_data = {
            'request': {},
            'pages': {},
            'page': {}
        }

        context = page_context(inner_function)(initial_data)

        self.assertDictEqual(context, initial_data)

    def test_get_page_from_context(self):
        # This might seem odd, but remember that we are in the News app, we're
        # trying to get the NewsFeed, not just the current page.

        context = {}
        kwargs = {}

        self.assertIsNone(get_page_from_context(context, kwargs))

        kwargs['page'] = self.homepage.pk

        self.assertIsNone(get_page_from_context(context, kwargs))

        del kwargs['page']
        context['page'] = self.homepage.pk
        self.assertIsNone(get_page_from_context(context, kwargs))

        del context['page']
        context['pages'] = Object()
        context['pages'].current = self.homepage.pk
        self.assertIsNone(get_page_from_context(context, kwargs))

    def test_takes_current_page(self):
        def inner_function(context, page):
            return page

        with self.assertRaises(VariableDoesNotExist):
            takes_current_page(inner_function)({})

        # Create a NewsFeed page.
        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(NewsFeed)

            self.page = Page.objects.create(
                title="News Feed",
                parent=self.homepage,
                content_type=content_type,
            )

            self.feed = NewsFeed.objects.create(
                page=self.page,
            )

        self.assertEqual(takes_current_page(inner_function)({}), self.page)

    def test_takes_article_page(self):
        def inner_function(context, article, page):
            self.assertEqual(context, {})
            self.assertEqual(article, self.article)
            self.assertEqual(page, self.page)
            return article

        self._create_feed_article()

        takes_article_page(inner_function)({}, self.article)

    def test_article_url(self):
        self._create_feed_article()

        url = article_url({}, self.article, page=self.page)
        self.assertEqual(url, '/news' + self.date_str + '/foo/')

    def test_article_archive_url(self):
        self._create_feed_article()
        archive_url = article_archive_url({'request': {}}, page=self.page)
        self.assertEqual(archive_url, '/news/')

    def test_category_url(self):
        self._create_feed_article()
        self.assertEqual(category_url({}, self.category, page=self.page), '/news/foo/')

    def test_article_year_archive_url(self):
        self._create_feed_article()
        url = article_year_archive_url({}, self.date.year, page=self.page)
        self.assertEqual(url, '/news/' + str(self.date.year) + '/')

    def test_article_day_archive_url(self):
        self._create_feed_article()
        url = article_day_archive_url({}, self.date, page=self.page)
        self.assertEqual(url, '/news' + self.date_str + '/')

    def test_article_date_list(self):
        self._create_feed_article()
        date_list = article_date_list({'request': {}}, page=self.page)

        self.assertEqual(date_list['request'], {})
        self.assertIsNone(date_list['current_year'])
        self.assertEqual(list(date_list['date_list']), [self.date.date().replace(day=1)])

        date_list = article_date_list({'request': {}, 'year': 1970}, page=self.page)

        self.assertEqual(date_list['request'], {})
        self.assertEqual(date_list['current_year'], 1970)
        self.assertEqual(list(date_list['date_list']), [self.date.date().replace(day=1)])

        date_list = article_date_list({'request': {}, 'year': self.date.date()}, page=self.page)

        self.assertEqual(date_list['request'], {})
        self.assertEqual(date_list['current_year'], self.date.date().year)
        self.assertEqual(list(date_list['date_list']), [self.date.date().replace(day=1)])

        date_list = article_date_list({'request': {}, 'month': self.date.date()}, page=self.page)

        self.assertEqual(date_list['request'], {})
        self.assertEqual(date_list['current_year'], self.date.date().year)
        self.assertEqual(list(date_list['date_list']), [self.date.date().replace(day=1)])

        date_list = article_date_list({'request': {}, 'day': self.date.date()}, page=self.page)

        self.assertEqual(date_list['request'], {})
        self.assertEqual(date_list['current_year'], self.date.date().year)
        self.assertEqual(list(date_list['date_list']), [self.date.date().replace(day=1)])

        date_list = article_date_list({'request': {}, 'article': self.article}, page=self.page)

        self.assertEqual(date_list['request'], {})
        self.assertEqual(date_list['current_year'], self.date.date().year)
        self.assertEqual(list(date_list['date_list']), [self.date.date().replace(day=1)])
