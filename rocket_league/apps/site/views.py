import json
from datetime import timedelta

from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.utils.timezone import now
from django.views.generic import RedirectView, TemplateView
from social.apps.django_app.default.models import UserSocialAuth

from ..replays.models import Goal, Player, Replay
from ..users.models import Profile
from .models import Patron, PatronTrial


class StatsView(TemplateView):
    template_name = 'site/stats.html'

    def get_stats(self, context, timeframe):
        if timeframe == 'all':
            since = now() - timedelta(days=36500)
        else:
            since = now() - timedelta(days=timeframe)

        # Number of replays total.
        context['number_of_replays_{}'.format(timeframe)] = Replay.objects.filter(
            timestamp__gte=since,
        ).count()

        # Unique players.
        context['unique_players_{}'.format(timeframe)] = Player.objects.filter(
            replay__timestamp__gte=since,
        ).distinct('player_name').order_by('player_name').count()

        # Unique Steam accounts.
        player_ids = Player.objects.filter(
            platform__in=['OnlinePlatform_Steam', '1'],
            replay__timestamp__gte=since,
        ).distinct('online_id').values_list('online_id', flat=True).order_by()

        social_auth_ids = []
        if timeframe == 'all':
            social_auth_ids = UserSocialAuth.objects.filter(
                provider='steam',
            ).distinct('uid').values_list('uid', flat=True).order_by()

        context['steam_accounts_{}'.format(timeframe)] = len(set(list(player_ids) + list(social_auth_ids)))

        # Number of goals scored.
        context['goals_scored_{}'.format(timeframe)] = Goal.objects.filter(
            replay__timestamp__gte=since,
        ).count()

        return context

    def get_context_data(self, **kwargs):
        context = super(StatsView, self).get_context_data(**kwargs)

        # Replays uploaded per day (for graph)
        context['replays_uploaded_per_day'] = Replay.objects.filter(
            processed=True,
            timestamp__gte=now() - timedelta(days=60)
        ).extra({
            'date': "date(timestamp)"
        }).values('date').annotate(
            created_count=Count('pk')
        ).order_by('date')

        # Overall stats #
        context = self.get_stats(context, 'all')

        # This week stats #
        context = self.get_stats(context, 7)

        # Today stats #
        context = self.get_stats(context, 1)

        return context


class StartTrialView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        # Check the eligibility.
        has_had_trial = self.request.user.profile.has_had_trial()

        if has_had_trial:
            # This user is not eligible for another trial.
            messages.error(self.request, "Unfortunately you are not currently eligible for a free trial.")
        else:
            # Activate a trial for this user.
            PatronTrial.objects.create(
                user=self.request.user,
                expiry_date=now() + timedelta(days=7),
            )
            messages.success(self.request, "Your free trial has been activated. You can make full use of all patron benefits for the next 7 days.")

        return reverse('replay:playback', kwargs=kwargs)


class StreamListView(TemplateView):

    template_name = 'site/stream_list.html'

    def clean_twitch_username(self, username):
        if 'twitch.tv' in username:
            return username.split('/')[-1]
        return username

    def get_queryset(self):
        # Get all of the active Patreons, then figure out if they have a Twitch
        # account listed.

        return Profile.objects.filter(
            patreon_email_address__in=Patron.objects.filter(
                pledge_declined_since=None,
                pledge_amount__gte=300,
            ).values_list('patron_email', flat=True),
        ).exclude(
            twitch_username='',
        )

    def get_context_data(self, **kwargs):
        context = super(StreamListView, self).get_context_data(**kwargs)

        query = Profile.objects.raw("""SELECT
  users_profile.id,
  twitch_username,
  CASE WHEN site_patron.pledge_amount >= 1000 THEN TRUE ELSE FALSE END featured
FROM users_profile
RIGHT JOIN site_patron on users_profile.patreon_email_address = site_patron.patron_email
WHERE
  users_profile.twitch_username != '' AND
  site_patron.pledge_amount >= 300 AND
  site_patron.pledge_declined_since IS NULL;""")

        context['usernames'] = []

        for row in query:
            context['usernames'].append({
                'username': self.clean_twitch_username(row.twitch_username).lower(),
                'featured': row.featured
            })

        context['usernames'] = json.dumps(context['usernames'])

        return context
