from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from ..models import Faq, Faqs

from cms import externals
from cms.apps.pages.models import Page


class ApplicationTestCase(TestCase):

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

        self.faq = Faq.objects.create(
            page=self.faq_page,
            question='What colour is the sky?',
            answer='Blue',
            url_title='what-colour-sky'
        )

        print self.faq_page.page.get_absolute_url()

    def test_faq_get_absolute_url(self):
        self.assertEqual(self.faq.get_absolute_url(), '/what-colour-sky/')

    def test_faq_unicode(self):
        self.assertEqual(self.faq.__unicode__(), 'What colour is the sky?')
