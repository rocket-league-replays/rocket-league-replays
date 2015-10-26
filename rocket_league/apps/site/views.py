from django.db.models import Count
from django.utils.timezone import now
from django.views.generic import TemplateView

from ..replays.models import Goal, Replay, Player

from social.apps.django_app.default.models import UserSocialAuth

from datetime import timedelta


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
            platform='OnlinePlatform_Steam',
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
