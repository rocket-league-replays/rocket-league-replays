from django.contrib import admin

from .models import Content, ContentColumn, Patron

from cms.apps.pages.admin import page_admin


class ContentColumnInline(admin.StackedInline):
    model = ContentColumn
    extra = 0
    max_num = 4

page_admin.register_content_inline(Content, ContentColumnInline)


@admin.register(Patron)
class PatronAdmin(admin.ModelAdmin):
    search_fields = ['pledge_id', 'patron_id', 'patron_email']
    list_display = ['pledge_id', 'patron_id', 'pledge_amount', 'patron_email']

    fieldsets = (
        ('Pledge', {
            'fields': ['pledge_id', 'pledge_amount', 'pledge_created',
                       'pledge_declined_since']
        }),
        ('Patron', {
            'fields': ['patron_id', 'patron_email']
        }),
    )
