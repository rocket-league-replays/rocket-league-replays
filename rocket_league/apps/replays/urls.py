from django.conf.urls import patterns, url

from . import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ReplayListView.as_view(), name='list'),
    url(r'^map/(?P<slug>[^/]+)/$', views.ReplayListView.as_view(), name='list'),

    url(r'^(?P<pk>\d+)/$', views.ReplayDetailView.as_view(), name='detail'),
    url(r'^(?P<replay_id>[a-f0-9]{8}-?4[a-f0-9]{3}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12})/$', views.ReplayDetailView.as_view(), name='detail'),

    url(r'^(?P<pk>\d+)/playback/$', views.ReplayPlaybackView.as_view(), name='playback'),
    url(r'^(?P<replay_id>[a-f0-9]{8}-?4[a-f0-9]{3}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12})/playback/$', views.ReplayPlaybackView.as_view(), name='playback'),
    url(r'^(?P<pk>\d+)/analysis/$', views.ReplayAnalysisView.as_view(), name='analysis'),

    url(r'^(?P<pk>\d+)/boost-analysis/$', views.ReplayBoostAnalysisView.as_view(), name='boost-analysis'),
    url(r'^(?P<replay_id>[a-f0-9]{8}-?4[a-f0-9]{3}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12})/boost-analysis/$', views.ReplayBoostAnalysisView.as_view(), name='boost-analysis'),

    url(r'^(?P<replay_id>[a-f0-9]{8}-?4[a-f0-9]{3}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12})/goal-hitmap/$', views.ReplayGoalHitmapView.as_view(), name='goal-hitmap'),

    url(r'^upload/$', views.ReplayCreateView.as_view(), name='upload'),
    url(r'^delete/(?P<pk>\d+)/$', views.ReplayDeleteView.as_view(), name='delete'),
    url(r'^update/(?P<pk>\d+)/$', views.ReplayUpdateView.as_view(), name='update'),
)
