from django.db.models import Q
from django.views.generic import DetailView, CreateView, UpdateView

from .forms import ReplayUploadForm, ReplayFilter, ReplayUpdateForm
from .models import Goal, Map, Player, Replay
from .serializers import GoalSerializer, MapSerializer, PlayerSerializer, ReplaySerializer
from ...utils.forms import AjaxableResponseMixin

from django_filters.views import FilterView
from rest_framework import viewsets

import re


class ReplayListView(FilterView):
    model = Replay
    paginate_by = 20
    template_name_suffix = '_list'
    filterset_class = ReplayFilter

    def get_queryset(self):
        qs = super(ReplayListView, self).get_queryset()

        qs = qs.exclude(
            Q(processed=False) |
            Q(replay_id='')
        )

        return qs


class ReplayDetailView(DetailView):
    model = Replay


class ReplayCreateView(AjaxableResponseMixin, CreateView):
    model = Replay
    form_class = ReplayUploadForm

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            form.instance.user = self.request.user

        return super(ReplayCreateView, self).form_valid(form)


class ReplayUpdateView(UpdateView):
    model = Replay
    form_class = ReplayUpdateForm
    template_name_suffix = '_update'

    def form_valid(self, form):
        # Delete all user-entered players.
        self.object.player_set.filter(user_entered=True).delete()

        player_field_match = re.compile('team_(0|1)_player_(0|1|2|3)')

        for field in form.cleaned_data:
            match = player_field_match.match(field)

            if match and form.cleaned_data[field]:
                Player.objects.create(
                    replay=self.object,
                    player_name=form.cleaned_data[field],
                    team=match.group(1),
                    user_entered=True,
                )

        return super(ReplayUpdateView, self).form_valid(form)

    def get_success_url(self):
        return self.request.path


# API ViewSets
class ReplayViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all processed replays in the system.
    """

    queryset = Replay.objects.filter(
        processed=True,
    )
    serializer_class = ReplaySerializer


class MapViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all maps in the system.
    """

    queryset = Map.objects.all()
    serializer_class = MapSerializer


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all players in all games. These values are not unique.
    """

    queryset = Player.objects.all()
    serializer_class = PlayerSerializer


class GoalViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Returns a list of all goals in all games.
    """

    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
