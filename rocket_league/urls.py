"""URL config for rocket_league project."""

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views import generic
from django.conf.urls.static import static

from cms.sitemaps import registered_sitemaps
from cms.views import TextTemplateView
from cms.forms import CMSPasswordChangeForm


admin.autodiscover()


urlpatterns = patterns(
    "",

    # Admin URLs.
    url(r'^admin/password_change/$', 'django.contrib.auth.views.password_change',
        {'password_change_form': CMSPasswordChangeForm}, name='password_change'),
    url(r'^admin/password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r"^admin/", include(admin.site.urls)),

    url(r'replays/', include('rocket_league.apps.replays.urls', namespace='replay')),

    # Permalink redirection service.
    url(r"^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$", "django.contrib.contenttypes.views.shortcut", name="permalink_redirect"),

    # Google sitemap service.
    url(r"^sitemap.xml$", "django.contrib.sitemaps.views.index", {"sitemaps": registered_sitemaps}),
    url(r"^sitemap-(?P<section>.+)\.xml$", "django.contrib.sitemaps.views.sitemap", {"sitemaps": registered_sitemaps}),

    # Basic robots.txt.
    url(r"^robots.txt$", TextTemplateView.as_view(template_name="robots.txt")),

    # There's no favicon here!
    url(r"^favicon.ico$", generic.RedirectView.as_view(permanent=True)),

    url('', include('social.apps.django_app.urls', namespace='social'))

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += patterns(
        "",
        url("^404/$", generic.TemplateView.as_view(template_name="404.html")),
        url("^500/$", generic.TemplateView.as_view(template_name="500.html")),
    )


handler500 = "cms.views.handler500"
