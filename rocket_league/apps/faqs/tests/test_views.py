from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.test.client import RequestFactory

from ..models import Faqs
from ..views import FaqListView

from cms import externals
from cms.apps.pages.models import Page
from cms.apps.pages.middleware import RequestPageManager


class FAQsTestCase(TestCase):

    def setUp(self):
        # Note: as this is the only page in the database, it's absolute URL
        # will simply be '/'

        with externals.watson.context_manager("update_index")():
            content_type = ContentType.objects.get_for_model(Faqs)
            self.page = Page.objects.create(
                content_type=content_type,
                title='Foo',
                url_title='foo',
            )

            self.faq_page = Faqs.objects.create(
                page=self.page,
            )

    def test_faq_list_view_get_paginate_by(self):
        def setup_view(view, request, *args, **kwargs):
            """Mimic as_view() returned callable, but returns view instance.

            args and kwargs are the same you would pass to ``reverse()``

            """
            view.request = request
            view.args = args
            view.kwargs = kwargs
            return view

        self.factory = RequestFactory()
        request = self.factory.get('/')

        # Set the pages attribute manually as middleware isn't run in tests.
        request.pages = RequestPageManager(request.path, request.path_info)

        view = FaqListView()
        view = setup_view(view, request)
        view.dispatch(view.request, *view.args, **view.kwargs)

        self.assertEqual(view.get_paginate_by(view.get_queryset()), 5)
