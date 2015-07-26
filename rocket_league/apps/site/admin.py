from django.contrib import admin

from .models import Content, ContentColumn

from cms.apps.pages.admin import page_admin


class ContentColumnInline(admin.StackedInline):
    model = ContentColumn
    extra = 0
    max_num = 4

page_admin.register_content_inline(Content, ContentColumnInline)
