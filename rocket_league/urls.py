"""URL config for rocket_league project."""

from cms.forms import CMSPasswordChangeForm
from cms.sitemaps import registered_sitemaps
from cms.views import TextTemplateView
from django.conf import settings
from django.conf.urls import include, patterns, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views import generic
from rest_framework import routers

from .apps.replays.views import (BodyViewSet, GoalViewSet, LatestUserReplay,
                                 MapViewSet, PlayerViewSet, ReplayViewSet,
                                 SeasonViewSet)
from .apps.users.views import StreamDataAPIView

admin.autodiscover()


router = routers.DefaultRouter()
router.register(r'maps', MapViewSet)
router.register(r'replays', ReplayViewSet)
router.register(r'players', PlayerViewSet)
router.register(r'goals', GoalViewSet)
router.register(r'seasons', SeasonViewSet)
router.register(r'bodies', BodyViewSet)


urlpatterns = patterns(
    "",

    # Admin URLs.
    url(r'^admin/password_change/$', 'django.contrib.auth.views.password_change',
        {'password_change_form': CMSPasswordChangeForm}, name='password_change'),
    url(r'^admin/password_change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),
    url(r"^admin/", include(admin.site.urls)),

    url(r'^replays/', include('rocket_league.apps.replays.urls', namespace='replay')),
    url(r'^replay-packs/', include('rocket_league.apps.replays.replaypack_urls', namespace='replaypack')),

    # Permalink redirection service.
    url(r"^r/(?P<content_type_id>\d+)-(?P<object_id>[^/]+)/$", "django.contrib.contenttypes.views.shortcut", name="permalink_redirect"),

    # Google sitemap service.
    url(r"^sitemap.xml$", "django.contrib.sitemaps.views.index", {"sitemaps": registered_sitemaps}),
    url(r"^sitemap-(?P<section>.+)\.xml$", "django.contrib.sitemaps.views.sitemap", {"sitemaps": registered_sitemaps}),

    # Basic robots.txt.
    url(r"^robots.txt$", TextTemplateView.as_view(template_name="robots.txt")),

    # There's no favicon here!
    url(r"^favicon.ico$", generic.RedirectView.as_view(url='/static/build/img/icons/favicon.ico', permanent=True)),

    url(r'^api/', include(router.urls)),
    url(r'^api/stream-data/(?P<user_id>\d+)/$', StreamDataAPIView.as_view(), name='stream-data'),
    url(r'^api/latest-replay/(?P<user_id>\d+)/$', LatestUserReplay.as_view(), name='latest-replay'),

    url(r'^api-docs/', include('rest_framework_swagger.urls')),

    url(r'^login/$', 'django.contrib.auth.views.login', name='auth_login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='auth_logout'),

    url(r'', include('rocket_league.apps.site.urls', namespace='site')),
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
