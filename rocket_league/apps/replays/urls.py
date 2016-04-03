from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ReplayListView.as_view(), name='list'),
    url(r'^map/(?P<slug>[^/]+)/$', views.ReplayListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', views.ReplayDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/playback/$', views.ReplayPlaybackView.as_view(), name='playback'),
    url(r'^(?P<pk>\d+)/analysis/$', views.ReplayAnalysisView.as_view(), name='analysis'),
    url(r'^upload/$', views.ReplayCreateView.as_view(), name='upload'),
    url(r'^delete/(?P<pk>\d+)/$', views.ReplayDeleteView.as_view(), name='delete'),
    url(r'^update/(?P<pk>\d+)/$', views.ReplayUpdateView.as_view(), name='update'),
)
