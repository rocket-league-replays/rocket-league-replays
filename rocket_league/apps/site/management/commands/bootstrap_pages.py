import os

from cms.apps.pages.models import Page
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.db.models.loading import get_model

def create_page(entry):
    print(f"Creating {entry['title']}")

    content_type = ContentType.objects.get_for_model(get_model(entry['content_type']))
    content_type.model_class().objects.create(
        page=Page.objects.create(
            title=entry['title'],
            slug=entry['slug'],
            content_type=content_type,
            parent=Page.objects.get_homepage() if Page.objects.exists() else None,
        ),
        **entry['content']
    )

class Command(BaseCommand):

    def handle(self, *args, **options):
        """Adds a few default pages to allow the site to load.

        By default `runserver` will show a technical 404 page when loading the
        homepage after initial migration. This management command adds a bunch
        of pages which match the structure of the live website."""

        Page.objects.all().delete()

        page_structure = [
            {
                'title': 'Rocket League Replays',
                'slug': 'homepage',
                'content_type': 'links.Link',
                'content': {
                    'link_url': '/replays/'
                }
            },
            {
                'title': 'Replays',
                'slug': 'replays',
                'content_type': 'links.Link',
                'content': {
                    'link_url': '/replays/'
                }
            },
            {
                'title': 'Replay Packs',
                'slug': 'replay-packs',
                'content_type': 'links.Link',
                'content': {
                    'link_url': '/replays-packs/'
                }
            },
            {
                'title': 'Upload Replays',
                'slug': 'upload-replay',
                'content_type': 'links.Link',
                'content': {
                    'link_url': '/replays/upload/'
                }
            },
            {
                'title': 'Streams',
                'slug': 'streams',
                'content_type': 'links.Link',
                'content': {
                    'link_url': '/streams/'
                }
            },
            {
                'title': 'API',
                'slug': 'api',
                'content_type': 'links.Link',
                'content': {
                    'link_url': '/api/'
                }
            },
        ]

        list(map(create_page, page_structure))
