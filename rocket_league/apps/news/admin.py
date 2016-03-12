"""Admin settings for the CMS news app."""

from cms import externals
from cms.admin import OnlineBaseAdmin, PageBaseAdmin
from django.conf import settings
from django.contrib import admin

from .models import STATUS_CHOICES, Article, Category, get_default_news_feed


class CategoryAdmin(PageBaseAdmin):

    """Admin settings for the Category model."""

    fieldsets = (
        PageBaseAdmin.TITLE_FIELDS,
        ("Content", {
            "fields": ("content_primary",),
        }),
        PageBaseAdmin.PUBLICATION_FIELDS,
        PageBaseAdmin.NAVIGATION_FIELDS,
        PageBaseAdmin.SEO_FIELDS,
    )


admin.site.register(Category, CategoryAdmin)


class ArticleAdminBase(PageBaseAdmin):

    """Admin settings for the Article model."""

    date_hierarchy = "date"

    search_fields = PageBaseAdmin.search_fields + ("content", "summary",)

    list_display = ("title", "date", "is_online",)

    list_filter = ("is_online", "categories", "status",)

    fieldsets = [
        (None, {
            "fields": ("title", "slug", "news_feed", "date", "status",),
        }),
        ("Content", {
            "fields": ("image", "content", "summary",),
        }),
        ("Publication", {
            "fields": ("categories", "authors", "is_online",),
            "classes": ("collapse",),
        }),
    ]

    fieldsets.extend(PageBaseAdmin.fieldsets)

    fieldsets.remove(PageBaseAdmin.TITLE_FIELDS)
    fieldsets.remove(OnlineBaseAdmin.PUBLICATION_FIELDS)

    raw_id_fields = ("image",)

    filter_horizontal = ("categories", "authors",)

    def save_related(self, request, form, formsets, change):
        """Saves the author of the article."""
        super(ArticleAdminBase, self).save_related(request, form, formsets, change)
        # For new articles, add in the current author.
        if not change and not form.cleaned_data["authors"]:
            form.instance.authors.add(request.user)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(ArticleAdminBase, self).get_fieldsets(request, obj)

        if not getattr(settings, "NEWS_APPROVAL_SYSTEM", False):
            for fieldset in fieldsets:
                fieldset[1]['fields'] = tuple(x for x in fieldset[1]['fields'] if x != 'status')

        return fieldsets

    def get_form(self, request, obj=None, **kwargs):
        form = super(ArticleAdminBase, self).get_form(request, obj, **kwargs)
        form.base_fields['news_feed'].initial = get_default_news_feed()
        return form

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        """
        Give people who have the permission to approve articles an extra
        option to change the status of an Article to approved
        """
        choices_list = STATUS_CHOICES
        if getattr(settings, "NEWS_APPROVAL_SYSTEM", False) and not request.user.has_perm('news.can_approve_articles'):
            choices_list = [x for x in STATUS_CHOICES if x[0] != 'approved']

        if db_field.name == "status":
            kwargs['choices'] = choices_list

        return super(ArticleAdminBase, self).formfield_for_choice_field(db_field, request, **kwargs)


if externals.reversion:
    class ArticleAdmin(ArticleAdminBase, externals.reversion["admin.VersionMetaAdmin"]):
        list_display = ArticleAdminBase.list_display + ("get_date_modified",)
else:
    class ArticleAdmin(ArticleAdminBase):
        pass

admin.site.register(Article, ArticleAdmin)
