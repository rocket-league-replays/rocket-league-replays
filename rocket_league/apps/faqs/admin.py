""" Admin settings for the faqs app """
from django.contrib import admin

from cms.admin import SearchMetaBaseAdmin

from .models import Faq


@admin.register(Faq)
class FaqAdmin(SearchMetaBaseAdmin):
    """ Admin settings for the Faq model """
    prepopulated_fields = {"url_title": ("question",)}

    fieldsets = (
        (None, {
            "fields": (
                "page",
                "question",
                "url_title",
                "answer",
                "order",
            )
        }),
        SearchMetaBaseAdmin.PUBLICATION_FIELDS,
        SearchMetaBaseAdmin.SEO_FIELDS,
    )
