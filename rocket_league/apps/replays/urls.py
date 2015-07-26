from django.conf.urls import patterns, url

from .views import ReplayListView, ReplayDetailView, ReplayCreateView

urlpatterns = patterns(
    '',
    url(r'^$', ReplayListView.as_view(), name='list'),
    url(r'^map/(?P<slug>[^/]+)/$', ReplayListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', ReplayDetailView.as_view(), name='detail'),
    url(r'^upload/$', ReplayCreateView.as_view(), name='upload'),
)
