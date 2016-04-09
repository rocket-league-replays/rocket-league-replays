import re

from braces.views import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView
from rest_framework import mixins, viewsets

from ...utils.forms import AjaxableResponseMixin
from .filters import ReplayFilter, ReplayPackFilter
from .forms import ReplayPackForm, ReplayUpdateForm
from .models import (Goal, Map, Player, Replay, ReplayPack, Season,
                     get_default_season)
from .serializers import (GoalSerializer, MapSerializer, PlayerSerializer,
                          ReplayCreateSerializer, ReplaySerializer,
                          SeasonSerializer)
from .templatetags.replays import boost_chart_data, process_boost_data


class ReplayListView(FilterView):
    model = Replay
    paginate_by = 30
    template_name_suffix = '_list'
    filterset_class = ReplayFilter

    def get_queryset(self):
        qs = super(ReplayListView, self).get_queryset()

        qs = qs.exclude(
            Q(processed=False) |
            Q(replay_id='')
        )

        if 'season' not in self.request.GET:
            # Default to the current season.
            qs = qs.filter(
                season_id=get_default_season()
            )
        else:
            qs = qs.filter(
                season_id=self.request.GET['season'] or get_default_season()
            )

        if 'order' in self.request.GET:
            qs = qs.order_by(*self.request.GET.getlist('order'))
        else:
            # TODO: Make a rating which combines these.
            qs = qs.extra(select={
                'timestamp__date': 'DATE(timestamp)'
            })
            qs = qs.order_by('-timestamp__date', '-average_rating')

        return qs

    def get_context_data(self, **kwargs):
        context = super(ReplayListView, self).get_context_data(**kwargs)

        context['filter'].form.fields['season'].choices = [
            choice for choice in
            context['filter'].form.fields['season'].choices
            if choice[0]
        ]

        context['filter'].form.initial = {
            'season': get_default_season()
        }
        return context


class ReplayDetailView(DetailView):
    model = Replay


class ReplayBoostAnalysisView(DetailView):
    model = Replay
    template_name_suffix = '_boost_analysis'

    def get_context_data(self, **kwargs):
        context = super(ReplayBoostAnalysisView, self).get_context_data(**kwargs)

        context['team_0_boost_consumed'] = 0
        context['team_1_boost_consumed'] = 0

        # Get the tabular data.
        for player in self.object.player_set.all():
            if not player.boost_data:
                player.boost_data = process_boost_data({}, obj=player)
                player.save()

            # Get the team boost data.
            if player.team == 0:
                context['team_0_boost_consumed'] += player.boost_data['boost_consumption']
            elif player.team == 1:
                context['team_1_boost_consumed'] += player.boost_data['boost_consumption']

        return context


class ReplayPlaybackView(DetailView):
    model = Replay
    template_name_suffix = '_playback'


class ReplayCreateView(AjaxableResponseMixin, CreateView):
    model = Replay
    fields = ['file']

    def form_invalid(self, form):
        import re
        results = re.search(r'\/replays\/(\d+)\/', form.errors['__all__'][0])

        if results:
            form.errors['errorText'] = form.errors['__all__'][0]
            form.errors['replayID'] = results.group(1)
            del form.errors['__all__']

        return super(ReplayCreateView, self).form_invalid(form)

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            form.instance.user = self.request.user

        return super(ReplayCreateView, self).form_valid(form)


class ReplayUpdateView(LoginRequiredMixin, UpdateView):
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


class ReplayDeleteView(DeleteView):
    model = Replay

    def get_success_url(self):
        return reverse('users:profile', kwargs={
            'username': self.request.user.username,
        })

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().user:
            raise PermissionDenied

        return super(ReplayDeleteView, self).dispatch(request, *args, **kwargs)


# Replay packs
class ReplayPackCreateView(LoginRequiredMixin, CreateView):
    model = ReplayPack
    form_class = ReplayPackForm
    template_name_suffix = '_create'

    def get_initial(self):
        initial = super(ReplayPackCreateView, self).get_initial()

        try:
            initial['replays'] = [int(val) for val in self.request.GET.getlist('replay_id')]
        except:
            pass

        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ReplayPackCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        kwargs = super(ReplayPackCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class ReplayPackUpdateView(LoginRequiredMixin, UpdateView):
    model = ReplayPack
    form_class = ReplayPackForm
    template_name_suffix = '_create'

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().user:
            raise PermissionDenied

        return super(ReplayPackUpdateView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(ReplayPackUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object.file.delete()
        return super(ReplayPackUpdateView, self).form_valid(form)


class ReplayPackDetailView(DetailView):
    model = ReplayPack


class ReplayPackListView(FilterView):
    model = ReplayPack
    paginate_by = 10
    template_name_suffix = '_list'
    filterset_class = ReplayPackFilter

    def get_queryset(self):
        qs = super(ReplayPackListView, self).get_queryset()
        qs = qs.exclude(
            replays__isnull=True,
        )
        return qs


class ReplayPackDeleteView(DeleteView):
    model = ReplayPack

    def get_success_url(self):
        return reverse('users:profile', kwargs={
            'username': self.request.user.username,
        })

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().user:
            raise PermissionDenied

        return super(ReplayPackDeleteView, self).dispatch(request, *args, **kwargs)


# API ViewSets
class ReplayViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    """
    Returns a list of all processed replays in the system. To filter to replays \
    owned by the currently logged in user, simply append ?owned to the URL.
    """

    queryset = Replay.objects.filter(
        processed=True,
    )
    serializer_class = ReplaySerializer

    serializer_action_classes = {
        'list': ReplaySerializer,
        'create': ReplayCreateSerializer,
    }

    def get_serializer_class(self):
        """
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class MyViewSet(MultiSerializerViewSetMixin, ViewSet):
            serializer_class = MyDefaultSerializer
            serializer_action_classes = {
               'list': MyListSerializer,
               'my_action': MyActionSerializer,
            }

            @action
            def my_action:
                ...

        If there's no entry for that action then just fallback to the regular
        get_serializer_class lookup: self.serializer_class, DefaultSerializer.

        Thanks gonz: http://stackoverflow.com/a/22922156/11440

        """
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(ReplayViewSet, self).get_serializer_class()

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `owned` query parameter in the URL.
        """
        queryset = Replay.objects.all()

        if 'owned' in self.request.query_params and self.request.user.is_authenticated():
            queryset = queryset.filter(
                user=self.request.user,
            )
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MapViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all maps in the system.
    """

    queryset = Map.objects.all()
    serializer_class = MapSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all seasons in the system.
    """

    queryset = Season.objects.all()
    serializer_class = SeasonSerializer


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
