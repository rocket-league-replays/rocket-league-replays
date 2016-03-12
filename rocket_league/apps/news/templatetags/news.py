"""Template tags used by the news module."""

from functools import wraps

from cms.apps.pages.models import Page
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils.html import escape

from ..models import Article, NewsFeed, get_default_news_page

register = template.Library()


def page_context(func):
    """Decorator for functions that pass on the current page into the next context."""

    @wraps(func)
    def do_page_context(context, *args, **kwargs):
        params = func(context, *args, **kwargs)
        params["request"] = context["request"]

        if "pages" in context:
            params["pages"] = context["pages"]
        if "page" in context:
            params["page"] = context["page"]

        return params

    return do_page_context


def get_page_from_context(context, kwargs):
    """Returns the current page based on the given template context."""
    page = None

    # Resolve the page.
    if "page" in kwargs:
        page = kwargs["page"]
    elif "page" in context:
        page = context["page"]
    elif "pages" in context:
        pages = context["pages"]
        page = pages.current

    # Adapt the page.
    if isinstance(page, int):
        page = Page.objects.get(id=page)
    if page and page.content_type_id != ContentType.objects.get_for_model(NewsFeed).id:
        page = get_default_news_page()

    return page


def takes_current_page(func):
    """Decorator for template tags that require the current page."""

    @wraps(func)
    def do_takes_current_page(context, *args, **kwargs):
        page = get_page_from_context(context, kwargs)

        if not page:
            page = get_default_news_page()
        if page is None:
            raise template.VariableDoesNotExist("Could not determine the current page from the template context.")
        kwargs["page"] = page

        return func(context, *args, **kwargs)

    return do_takes_current_page


def takes_article_page(func):
    """Decorator for template tags that require a page for an article."""

    @wraps(func)
    def do_takes_article_page(context, article, *args, **kwargs):
        page = get_page_from_context(context, kwargs)

        if not page or page.id != article.news_feed_id:
            page = article.news_feed.page

        kwargs["page"] = page

        return func(context, article, *args, **kwargs)

    return do_takes_article_page


@register.simple_tag(takes_context=True)
@takes_article_page
def article_url(context, article, page):
    """Renders the URL for an article."""
    return escape(article._get_permalink_for_page(page))


@register.simple_tag(takes_context=True)
@takes_current_page
def article_archive_url(context, page):
    """Renders the URL for the current article archive."""
    return escape(page.reverse("article_archive"))


@register.simple_tag(takes_context=True)
@takes_current_page
def category_url(context, category, page):
    """Renders the URL for the given category."""
    return escape(category._get_permalink_for_page(page))


@register.simple_tag(takes_context=True)
@takes_current_page
def article_year_archive_url(context, year, page):
    """Renders the year archive URL for the given year."""
    return escape(page.reverse("article_year_archive", kwargs={
        "year": year,
    }))


@register.simple_tag(takes_context=True)
@takes_current_page
def article_day_archive_url(context, date, page):
    """Renders the month archive URL for the given date."""
    return escape(page.reverse("article_day_archive", kwargs={
        "year": date.year,
        "month": date.strftime("%b").lower(),
        "day": date.day,
    }))


@register.inclusion_tag("news/includes/article_date_list.html", takes_context=True)
@page_context
@takes_current_page
def article_date_list(context, page):
    """Renders a list of dates."""
    date_list = Article.objects.filter(
        news_feed_id=page.id,
    ).dates("date", "month").order_by("-date")

    # Resolve the current year.
    current_year = context.get("year", None)

    if current_year is not None:
        try:
            current_year = int(current_year)
        except TypeError:
            current_year = int(current_year.year)
    else:
        current_month = context.get("month", None)

        if current_month is not None:
            current_year = current_month.year
        else:
            current_day = context.get("day", None)

            if current_day is not None:
                current_year = current_day.year
            else:
                current_article = context.get("article", None)

                if current_article is not None:
                    current_year = current_article.date.year

    return {
        "date_list": date_list,
        "current_year": current_year,
    }
