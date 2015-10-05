from django.conf.urls import patterns, url

import views

urlpatterns = patterns(
    '',
    url(r'^user/(?P<username>[^/]+)/$', views.PublicProfileView.as_view(), name='profile'),
    url(r'^profile/$', views.UserReplaysView.as_view(), name='profile'),
    url(r'^profile/replay-packs/$', views.UserReplayPacksView.as_view(), name='replay_packs'),
    url(r'^profile/desktop-application/$', views.UserDesktopApplicationView.as_view(), name='desktop_application'),
    url(r'^profile/rank-tracker/$', views.UserRankTrackerView.as_view(), name='rank_tracker'),
    url(r'^profile/settings/$', views.UserSettingsView.as_view(), name='settings'),
)
