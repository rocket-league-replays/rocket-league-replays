from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ReplayListView.as_view(), name='list'),
    url(r'^map/(?P<slug>[^/]+)/$', views.ReplayListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', views.ReplayDetailView.as_view(), name='detail'),
    url(r'^upload/$', views.ReplayCreateView.as_view(), name='upload'),
    url(r'^update/(?P<pk>\d+)/$', views.ReplayUpdateView.as_view(), name='update'),
)
