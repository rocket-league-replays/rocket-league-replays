from cms import externals
from cms.apps.pages.middleware import RequestPageManager
from cms.apps.pages.models import Page
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory, TestCase
from django.utils.timezone import now
from django.views import generic

from ..models import Article, Category, NewsFeed
from ..views import (ArticleCategoryArchiveView, ArticleDetailView,
                     ArticleFeedView, ArticleListMixin)


class TestView(ArticleListMixin, generic.YearArchiveView):
    pass


class TestViews(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

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
                slug='news',
                content_type=content_type,
            )

            self.feed = NewsFeed.objects.create(
                page=self.page,
            )

            self.article = Article.objects.create(
                news_feed=self.feed,
                title='Foo',
                slug='foo',
                date=self.date,
            )

            self.category = Category.objects.create(
                title='Foo',
                slug='foo'
            )
            self.article.categories.add(self.category)

    def test_articlelistmixin_get_paginate_by(self):
        view = ArticleListMixin()
        view.request = self.factory.get('/')
        view.request.pages = RequestPageManager(view.request)

        self.assertEqual(view.get_paginate_by(None), 5)

    def test_articlelistmixin_get_context_data(self):
        view = TestView()
        view.request = self.factory.get('/')
        view.request.pages = RequestPageManager(view.request)
        view.object_list = Article.objects.all()
        view.kwargs = {}

        data = view.get_context_data()

        self.assertEqual(list(data['article_list']), [self.article])
        self.assertEqual(list(data['object_list']), [self.article])
        self.assertEqual(list(data['category_list']), [self.category])
        self.assertEqual(repr(data['page_obj']), '<Page 1 of 1>')
        self.assertFalse(data['is_paginated'])

    def test_articlelistmixin_get_queryset(self):
        view = TestView()
        view.request = self.factory.get('/')
        view.request.pages = RequestPageManager(view.request)

        self.assertListEqual(list(view.get_queryset()), [self.article])

    def test_articlefeedview_get(self):
        view = ArticleFeedView()
        view.request = self.factory.get('/news/feed/')
        view.request.pages = RequestPageManager(view.request)

        get = view.get(view.request)

        self.assertEqual(get.status_code, 200)

        # Handle single and double digit dates.
        self.assertIn(get['Content-Length'], ['388', '389'])

        self.assertEqual(get['Content-Type'], 'application/rss+xml; charset=utf-8')

    def test_articledetailview_get_context_data(self):
        view = ArticleDetailView()
        view.request = self.factory.get('/news/foo/')
        view.request.pages = RequestPageManager(view.request)
        view.object = self.article

        data = view.get_context_data()

        self.assertEqual(data['meta_description'], '')
        self.assertEqual(data['robots_follow'], True)
        self.assertEqual(list(data['category_list']), [self.category])
        self.assertEqual(data['robots_index'], True)
        self.assertEqual(data['title'], 'Foo')
        self.assertEqual(data['object'], self.article)
        self.assertEqual(data['robots_archive'], True)
        self.assertEqual(data['header'], 'Foo')
        self.assertEqual(data['prev_article'], None)
        self.assertEqual(data['article'], self.article)
        self.assertEqual(data['next_article'], None)
        self.assertEqual(data['view'], view)

    def test_articlecategoryarchiveview_get_queryset(self):
        view = ArticleCategoryArchiveView()
        view.request = self.factory.get('')
        view.request.pages = RequestPageManager(view.request)
        view.object = self.category

        self.assertListEqual(list(view.get_queryset()), [self.article])

    def test_articlecategoryarchiveview_get_context_data(self):
        view = ArticleCategoryArchiveView()
        view.request = self.factory.get('')
        view.request.pages = RequestPageManager(view.request)
        view.object = self.category
        view.object_list = Article.objects.all()
        view.kwargs = {}

        data = view.get_context_data()

        self.assertEqual(data['meta_description'], '')
        self.assertEqual(data['robots_follow'], True)
        self.assertEqual(list(data['category_list']), [self.category])
        self.assertEqual(data['robots_index'], True)
        self.assertEqual(data['title'], 'Foo')
        self.assertEqual(list(data['object_list']), [self.article])
        self.assertEqual(data['robots_archive'], True)
        self.assertEqual(data['header'], 'Foo')
        self.assertEqual(list(data['article_list']), [self.article])
        self.assertEqual(repr(data['page_obj']), '<Page 1 of 1>')
        self.assertEqual(data['category'], self.category)
        self.assertEqual(data['view'], view)

    def test_articlecategoryarchiveview_dispatch(self):
        view = ArticleCategoryArchiveView()
        view.request = self.factory.get('')
        view.request.pages = RequestPageManager(view.request)
        view.kwargs = {}

        dispatch = view.dispatch(view.request, slug='foo')
        self.assertListEqual(dispatch.template_name, [
            'news/article_category_archive.html',
            'news/article_list.html'
        ])
        self.assertEqual(dispatch.status_code, 200)
