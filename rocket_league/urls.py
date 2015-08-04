"""URL config for rocket_league project."""

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.contrib import admin
from django.views import generic
from django.conf.urls.static import static

from cms.sitemaps import registered_sitemaps
from cms.views import TextTemplateView
from cms.forms import CMSPasswordChangeForm

from .apps.replays.views import GoalViewSet, ReplayViewSet, PlayerViewSet, MapViewSet
from .apps.site.forms import RegistrationForm

from registration.backends.simple.views import RegistrationView
from rest_framework import routers


admin.autodiscover()


router = routers.DefaultRouter()
router.register(r'maps', MapViewSet)
router.register(r'replays', ReplayViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'goals', GoalViewSet)


urlpatterns = patterns(
    "",

    # Admin URLs.
    url(r'^admin/password_change/$', 'django.contrib.auth.views.password_change',
        {'password_change_form': CMSPasswordChangeForm}, name='password_change'),
    url(r'^admin/password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r"^admin/", include(admin.site.urls)),

    url(r'^replays/', include('rocket_league.apps.replays.urls', namespace='replay')),

    # Permalink redirection service.
    url(r"^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$", "django.contrib.contenttypes.views.shortcut", name="permalink_redirect"),

    # Google sitemap service.
    url(r"^sitemap.xml$", "django.contrib.sitemaps.views.index", {"sitemaps": registered_sitemaps}),
    url(r"^sitemap-(?P<section>.+)\.xml$", "django.contrib.sitemaps.views.sitemap", {"sitemaps": registered_sitemaps}),

    # Basic robots.txt.
    url(r"^robots.txt$", TextTemplateView.as_view(template_name="robots.txt")),

    # There's no favicon here!
    url(r"^favicon.ico$", generic.RedirectView.as_view(permanent=True)),

    url(r'^api/', include(router.urls)),
    url(r'^api-docs/', include('rest_framework_swagger.urls')),

    url(r'^register/$', RegistrationView.as_view(form_class=RegistrationForm), name='register'),
    url(r'', include('registration.auth_urls', namespace='auth')),
    url(r'', include('rocket_league.apps.users.urls', namespace='users')),

    url('', include('social.apps.django_app.urls', namespace='social'))

) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


if settings.DEBUG:
    urlpatterns += patterns(
        "",
        url("^404/$", generic.TemplateView.as_view(template_name="404.html")),
        url("^500/$", generic.TemplateView.as_view(template_name="500.html")),
    )


handler500 = "cms.views.handler500"
