from django.conf.urls import patterns, url

from .views import ProfileView

urlpatterns = patterns(
    '',
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
)
