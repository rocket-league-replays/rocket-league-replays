"""URLs used by the CMS news app."""

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^$", views.ArticleArchiveView.as_view(), name="article_archive"),
    url(r"^feed/$", views.ArticleFeedView.as_view(), name="article_feed"),
    url(r"^(?P<year>\d+)/$", views.ArticleYearArchiveView.as_view(), name="article_year_archive"),
    url(r"^(?P<year>\d+)/(?P<month>\w+)/$", views.ArticleMonthArchiveView.as_view(), name="article_month_archive"),
    url(r"^(?P<year>\d+)/(?P<month>\w+)/(?P<day>\d+)/$", views.ArticleDayArchiveView.as_view(), name="article_day_archive"),
    url(r"^(?P<year>\d+)/(?P<month>\w+)/(?P<day>\d+)/(?P<slug>[^/]+)/$", views.ArticleDetailView.as_view(), name="article_detail"),
    url(r"^(?P<slug>[^/]+)/$", views.ArticleCategoryArchiveView.as_view(), name="article_category_archive"),
]
