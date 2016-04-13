from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^user/(?P<username>[^/]+)/$', views.PublicProfileView.as_view(), name='profile'),
    url(r'^steam/(?P<steam_id>[^/]+)/$', views.SteamView.as_view(), name='steam'),
    url(r'^settings/patreon/$', views.PatreonSettingsView.as_view(), name='patreon'),
    url(r'^profile/settings/$', views.UserSettingsView.as_view(), name='settings'),
    url(r'^user/stream/settings/$', views.StreamSettingsView.as_view(), name='stream_settings'),
)
