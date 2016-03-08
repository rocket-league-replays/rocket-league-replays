"""Models used by the CMS news app."""
from cms import externals, sitemaps
from cms.apps.media.models import ImageRefField
from cms.apps.pages.models import ContentBase, Page
from cms.models import (HtmlField, OnlineBaseManager, PageBase,
                        PageBaseSearchAdapter)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class NewsFeed(ContentBase):

    """A stream of news articles."""

    icon = "news/img/news-feed.png"

    # The heading that the admin places this content under.
    classifier = "syndication"

    # The urlconf used to power this content's views.
    urlconf = "rocket_league.apps.news.urls"

    content_primary = HtmlField(
        "primary content",
        blank=True
    )

    per_page = models.IntegerField(
        "articles per page",
        default=5,
        blank=True,
        null=True,
    )

    def __unicode__(self):
        return self.page.title


def get_default_news_page():
    """Returns the default news page."""
    try:
        return Page.objects.filter(
            content_type=ContentType.objects.get_for_model(NewsFeed),
        ).order_by("left")[0]
    except IndexError:
        return None


def get_default_news_feed():
    """Returns the default news feed for the site."""
    page = get_default_news_page()
    if page:
        return page.content.pk
    return None


class Category(PageBase):

    """A category for news articles."""

    content_primary = HtmlField(
        "primary content",
        blank=True
    )

    def _get_permalink_for_page(self, page):
        """Returns the URL for this category for the given page."""
        return page.reverse("article_category_archive", kwargs={
            "slug": self.slug,
        })

    def _get_permalinks(self):
        """Returns a dictionary of all permalinks for the given category."""
        pages = Page.objects.filter(
            id__in=Article.objects.filter(
                categories=self
            ).values_list("news_feed_id", flat=True)
        )
        return dict(
            (
                "page_{id}".format(id=page.id), self._get_permalink_for_page(page))
            for page in pages
        )

    def __unicode__(self):
        return self.short_title or self.title

    class Meta:
        verbose_name_plural = "categories"
        unique_together = (("slug",),)
        ordering = ("title",)


class CategoryHistoryLinkAdapter(externals.historylinks.HistoryLinkAdapter):

    """History link adapter for category models."""

    def get_permalinks(self, obj):
        """Returns all permalinks for the given category."""
        return obj._get_permalinks()


externals.historylinks("register", Category, CategoryHistoryLinkAdapter)


class ArticleManager(OnlineBaseManager):

    """Manager for Article models."""

    def select_published(self, queryset):
        queryset = super(ArticleManager, self).select_published(queryset)
        queryset = queryset.filter(
            date__lte=timezone.now(),
        )
        if getattr(settings, "NEWS_APPROVAL_SYSTEM", False):
            queryset = queryset.filter(
                status='approved'
            )
        return queryset

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('submitted', 'Submitted for approval'),
    ('approved', 'Approved')
]


class Article(PageBase):

    """A news article."""

    objects = ArticleManager()

    news_feed = models.ForeignKey(
        NewsFeed,
        null=True,
        blank=False,
    )

    date = models.DateField(
        db_index=True,
        default=timezone.now,
    )

    image = ImageRefField(
        blank=True,
        null=True,
    )

    content = HtmlField(
        blank=True,
    )

    summary = HtmlField(
        blank=True,
    )

    categories = models.ManyToManyField(
        Category,
        blank=True,
    )

    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
    )

    status = models.CharField(
        max_length=100,
        choices=STATUS_CHOICES,
        default='draft'
    )

    def _get_permalink_for_page(self, page):
        """Returns the URL of this article for the given news feed page."""
        return page.reverse("article_detail", kwargs={
            "year": self.date.year,
            "month": self.date.strftime("%b").lower(),
            "day": self.date.day,
            "slug": self.slug,
        })

    def get_absolute_url(self):
        """Returns the URL of the article."""
        return self._get_permalink_for_page(self.news_feed.page)

    def __unicode__(self):
        return self.short_title or self.title

    class Meta:
        unique_together = (("news_feed", "date", "slug",),)
        ordering = ("-date",)
        permissions = (
            ("can_approve_articles", "Can approve articles"),
        )


externals.historylinks("register", Article)

sitemaps.register(Article)

externals.watson("register", Article, adapter_cls=PageBaseSearchAdapter)
