""" URLs used by the faqs app """
from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r"^$", views.FaqListView.as_view(), name="faq_list"),
    url(r"^(?P<faq_title>[\w-]+)/$", views.FaqView.as_view(), name="faq"),
)
