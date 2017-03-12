from django.conf.urls import patterns, url
from django.views.generic import RedirectView

from . import views

urlpatterns = patterns(
    '',
    url(r'^user/(?P<username>[^/]+)/$', views.PublicProfileView.as_view(), name='profile'),

    url(r'^(?P<platform>(steam|ps4|xboxone))/(?P<player_id>[^/]+)/$', views.PlayerView.as_view(), name='player'),

    url(r'^settings/$', views.SettingsView.as_view(), name='settings'),
    url(r'^settings/patreon/$', RedirectView.as_view(pattern_name='users:settings', permanent=False), name='patreon'),
    url(r'^profile/settings/$', views.UserSettingsView.as_view(), name='password'),
    url(r'^user/stream/settings/$', views.StreamSettingsView.as_view(), name='stream_settings'),
    url(r'^user/stream/(?P<user_id>\d+)/(?P<method>\bbasic\b)/$', views.StreamDataView.as_view(), name='stream'),
    url(r'^user/stream/(?P<user_id>\d+)/(?P<method>\bsingle\b)/(?P<field>[^/]+)/$', views.StreamDataView.as_view(), name='stream'),
    url(r'^user/stream/(?P<user_id>\d+)/(?P<method>\bcustom\b)/(?P<template>[^/]+)/$', views.StreamDataView.as_view(), name='stream'),
)
