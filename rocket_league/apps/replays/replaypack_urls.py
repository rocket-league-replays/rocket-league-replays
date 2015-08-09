from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^$', views.ReplayPackListView.as_view(), name='list'),
    url(r'^(?P<pk>\d+)/$', views.ReplayPackDetailView.as_view(), name='detail'),
    url(r'^create/$', views.ReplayPackCreateView.as_view(), name='create'),
    url(r'^update/(?P<pk>\d+)/$', views.ReplayPackUpdateView.as_view(), name='update'),
    url(r'^delete/(?P<pk>\d+)/$', views.ReplayPackDeleteView.as_view(), name='delete'),
    url(r'^download/(?P<pk>\d+)/$', views.ReplayPackDeleteView.as_view(), name='download'),
)
