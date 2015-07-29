from django.db.models import Q
from django.views.generic import DetailView, CreateView

from .forms import ReplayUploadForm, ReplayFilter
from .models import Goal, Map, Player, Replay
from .serializers import GoalSerializer, MapSerializer, PlayerSerializer, ReplaySerializer

from django_filters.views import FilterView
from rest_framework import viewsets


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


class ReplayCreateView(CreateView):
    model = Replay
    form_class = ReplayUploadForm


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
