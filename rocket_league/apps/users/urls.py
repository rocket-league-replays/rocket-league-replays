from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^user/(?P<username>[^/]+)/$', views.PublicProfileView.as_view(), name='profile'),
)
