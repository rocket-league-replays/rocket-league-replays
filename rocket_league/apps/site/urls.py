from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^stats/$', views.StatsView.as_view(), name="stats"),
    url(r'^start-trial/(?P<pk>\d+)/$', views.StartTrialView.as_view(), name="start-trial"),
]
