from cms import externals
from cms.apps.pages.models import Page
from django.contrib.admin.sites import AdminSite
from django.contrib.contenttypes.models import ContentType
from django.forms.models import save_instance
from django.test import RequestFactory, TestCase
from django.utils.timezone import now

from ..admin import ArticleAdminBase
from ..models import Article, Category, NewsFeed, get_default_news_feed


class MockSuperUser(object):
    pk = 1

    def has_perm(self, perm):
        return True


class TestArticleAdminBase(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.article_admin = ArticleAdminBase(Article, self.site)

        self.factory = RequestFactory()
        self.request = self.factory.get('/')

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

            self.category = Category.objects.create(
                slug='foo'
            )

            self.article = Article.objects.create(
                news_feed=self.feed,
                title='Foo',
                slug='foo',
                date=self.date,
            )

    def test_articleadminbase_save_related(self):
        form = self.article_admin.get_form(self.request, obj=self.article)({
            'date': self.date,
            'news_feed': self.feed.pk,
            'slug': 'bar',
            'title': 'Bar'
        })
        self.assertTrue(form.is_valid())

        save_instance(form, self.article, commit=False)
        formsets = self.article_admin.get_formsets_with_inlines(self.request)
        self.article_admin.save_related(self.request, form, formsets, True)

        form.save()
        self.request.user = MockSuperUser().pk
        self.article_admin.save_related(self.request, form, formsets, False)

    def test_articleadminbase_formfield_for_choice_field(self):
        formfield = self.article_admin.formfield_for_choice_field(self.article._meta.get_field('status'), self.request)
        self.assertListEqual(formfield.choices, [
            ('draft', 'Draft'),
            ('submitted', 'Submitted for approval'),
            ('approved', 'Approved')
        ])

        self.request.user = MockSuperUser()

        with self.settings(NEWS_APPROVAL_SYSTEM=True):
            formfield = self.article_admin.formfield_for_choice_field(self.article._meta.get_field('status'), self.request)

        self.assertListEqual(formfield.choices, [
            ('draft', 'Draft'),
            ('submitted', 'Submitted for approval'),
            ('approved', 'Approved')
        ])

        self.request.user.has_perm = lambda x: False
        with self.settings(NEWS_APPROVAL_SYSTEM=True):
            formfield = self.article_admin.formfield_for_choice_field(self.article._meta.get_field('status'), self.request)

        self.assertListEqual(formfield.choices, [
            ('draft', 'Draft'),
            ('submitted', 'Submitted for approval'),
        ])

    def test_articleadminbase_get_form(self):
        form = self.article_admin.get_form(self.request, obj=None)
        default_feed = get_default_news_feed()
        self.assertTrue("news_feed" in form.base_fields)
        self.assertEqual(default_feed, form.base_fields["news_feed"].initial)
