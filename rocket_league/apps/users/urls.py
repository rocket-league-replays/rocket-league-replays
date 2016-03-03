from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^user/(?P<username>[^/]+)/$', views.PublicProfileView.as_view(), name='profile'),
    url(r'^steam/(?P<steam_id>[^/]+)/$', views.SteamView.as_view(), name='steam'),
    url(r'^profile/settings/$', views.UserSettingsView.as_view(), name='settings'),
)
