""" Models used by the faqs app. """
from django.db import models

from cms.apps.pages.models import ContentBase
from cms.models import SearchMetaBase, HtmlField

import watson


class Faqs(ContentBase):
    """ A base for Faq's """

    # The heading that the admin places this content under.
    classifier = "apps"

    # The urlconf used to power this content's views.
    urlconf = "rocket_league.apps.faqs.urls"

    standfirst = models.TextField(
        blank=True,
        null=True
    )

    per_page = models.IntegerField(
        "faqs per page",
        default=5,
        blank=True,
        null=True
    )


class Faq(SearchMetaBase):
    """ An FAQ """
    page = models.ForeignKey(
        Faqs
    )

    question = models.CharField(
        max_length=256
    )

    answer = HtmlField()

    url_title = models.CharField(
        max_length=256,
        unique=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __unicode__(self):
        return self.question

    class Meta:
        verbose_name = "faq"
        verbose_name_plural = "faqs"
        ordering = ['order', 'id', 'question']

    def get_absolute_url(self):
        """ Gets the url of a Faq

            Returns:
                url of Person

        """
        return "{}{}/".format(
            self.page.page.get_absolute_url(),
            self.url_title
        )

watson.register(Faq)
