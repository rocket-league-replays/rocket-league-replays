import logging
import os
import re

from braces.views import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  RedirectView, UpdateView)
from django_filters.views import FilterView
from rest_framework import mixins, views, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from . import serializers
from ...utils.forms import AjaxableResponseMixin
from ..users.models import User
from .filters import ReplayFilter, ReplayPackFilter
from .forms import ReplayPackForm, ReplayUpdateForm
from .models import (PRIVACY_PRIVATE, PRIVACY_PUBLIC, PRIVACY_UNLISTED,
                     Component, Goal, Map, Player, Replay, ReplayPack, Season,
                     get_default_season)
from .tasks import process_netstream
from .templatetags.replays import process_boost_data

logger = logging.getLogger('rocket_league')

class ReplayListView(FilterView):
    model = Replay
    paginate_by = 30
    template_name_suffix = '_list'
    filterset_class = ReplayFilter

    def get_queryset(self):
        qs = super(ReplayListView, self).get_queryset()

        qs = qs.exclude(
            Q(processed=False) |
            Q(replay_id='') |
            Q(team_sizes=None)
        )

        if 'season' not in self.request.GET:
            # Default to the current season.
            qs = qs.filter(
                season_id=get_default_season()
            )
        else:
            try:
                season_id = int(self.request.GET['season'])
            except ValueError:
                season_id = get_default_season()

            qs = qs.filter(
                season_id=season_id,
            )

        if 'order' in self.request.GET:
            qs = qs.order_by(*self.request.GET.getlist('order'))
        else:
            # TODO: Make a rating which combines these.
            qs = qs.extra(select={
                'timestamp__date': 'DATE(timestamp)'
            })
            qs = qs.order_by('-timestamp__date', '-average_rating')

        # Limit to public games, or unlisted / private games uploaded by the user.
        if self.request.user.is_authenticated():
            qs = qs.filter(
                Q(privacy=PRIVACY_PUBLIC) | Q(user=self.request.user)
            )
        else:
            qs = qs.filter(
                privacy=PRIVACY_PUBLIC,
            )
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


class ReplayUUIDMixin(DetailView):

    def dispatch(self, request, *args, **kwargs):
        from django.shortcuts import redirect
        from django.core.urlresolvers import resolve

        resolved_url = resolve(request.path)

        if 'pk' in kwargs:
            obj = get_object_or_404(Replay, pk=self.kwargs['pk'])

            if obj.replay_id:
                return redirect(
                    'replay:{}'.format(
                        resolved_url.url_name
                    ),
                    permanent=True,
                    replay_id=re.sub(r'([A-F0-9]{8})([A-F0-9]{4})([A-F0-9]{4})([A-F0-9]{4})([A-F0-9]{12})', r'\1-\2-\3-\4-\5', obj.replay_id).lower()
                )

        if 'replay_id' in kwargs and '-' not in kwargs['replay_id']:
            return redirect(
                'replay:{}'.format(
                    resolved_url.url_name
                ),
                permanent=True,
                replay_id=re.sub(r'([A-F0-9]{8})([A-F0-9]{4})([A-F0-9]{4})([A-F0-9]{4})([A-F0-9]{12})', r'\1-\2-\3-\4-\5', kwargs['replay_id'].upper()).lower()
            )

        return super(ReplayUUIDMixin, self).dispatch(request, *args, **kwargs)

    def get_object(self):
        replay_id = ''

        if 'replay_id' in self.kwargs:
            replay_id = self.kwargs['replay_id'].replace('-', '').upper()

        try:
            if 'replay_id' in self.kwargs:
                obj = get_object_or_404(Replay, replay_id=replay_id)
            elif 'pk' in self.kwargs:
                obj = get_object_or_404(Replay, pk=self.kwargs['pk'])
        except Replay.MultipleObjectsReturned:
            replays = Replay.objects.filter(
                replay_id=replay_id,
            )[1:]

            for replay in replays:
                replay.delete()

            obj = get_object_or_404(Replay, replay_id=replay_id)

        # Ensure the current user is allowed to view this replay.
        if obj.privacy in [PRIVACY_PUBLIC, PRIVACY_UNLISTED]:
            return obj

        if obj.privacy == PRIVACY_PRIVATE:
            if not self.request.user.is_authenticated():
                raise Http404

            if self.request.user != obj.user:
                raise Http404

        return obj


class ReplayDetailView(ReplayUUIDMixin):
    model = Replay


class ReplayAnalysisView(RedirectView):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        return reverse('replay:playback', kwargs=kwargs)


class ReplayBoostAnalysisView(ReplayUUIDMixin):
    model = Replay
    template_name_suffix = '_boost_analysis'

    def get_context_data(self, **kwargs):
        context = super(ReplayBoostAnalysisView, self).get_context_data(**kwargs)

        CACHE_KEY_0 = 'replay_boost_context_{}_team_0'.format(self.object.pk)
        CACHE_KEY_1 = 'replay_boost_context_{}_team_1'.format(self.object.pk)

        cached_data_0 = cache.get(CACHE_KEY_0)
        cached_data_1 = cache.get(CACHE_KEY_1)

        context['team_0_boost_consumed'] = 0
        context['team_1_boost_consumed'] = 0

        if cached_data_0 and cached_data_1:
            context['team_0_boost_consumed'] = cached_data_0
            context['team_1_boost_consumed'] = cached_data_1
            return context

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

        cache.set(CACHE_KEY_0, context['team_0_boost_consumed'], 3600)
        cache.set(CACHE_KEY_1, context['team_1_boost_consumed'], 3600)

        return context


class ReplayPlaybackView(ReplayUUIDMixin):
    model = Replay
    template_name_suffix = '_playback'


class ReplayCreateView(AjaxableResponseMixin, CreateView):
    model = Replay
    fields = ['file']

    def form_invalid(self, form):
        import re

        if '__all__' in form.errors:
            results = re.search(r'\/replays\/(\d+)\/', form.errors['__all__'][0])

            if results:
                form.errors['errorText'] = form.errors['__all__'][0]
                form.errors['replayID'] = results.group(1)
                del form.errors['__all__']

        return super(ReplayCreateView, self).form_invalid(form)

    def form_valid(self, form):
        if self.request.user.is_authenticated():
            form.instance.user = self.request.user

            # Set the privacy level according to this user's settings.
            form.instance.privacy = self.request.user.profile.privacy

        response = super(ReplayCreateView, self).form_valid(form)

        # Add the replay to the netstream processing queue.
        try:
            if os.getenv('DISABLE_REDIS'):
                process_netstream(self.object.pk)
            else:
                process_netstream.apply_async([self.object.pk], queue=self.object.queue_priority)
        except:
            logger.exception('ReplayCreateView.form_valid parse failed')

        return response


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


class ReplayNetstreamParseView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        replay_obj = Replay.objects.get(pk=kwargs['pk'])

        if settings.DEBUG:
            replay_obj.processed = False
            replay_obj.crashed_heatmap_parser = False
            replay_obj.save(parse_netstream=True)

        return replay_obj.get_absolute_url()

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

        # Set the privacy level according to this user's settings.
        form.instance.privacy = self.request.user.profile.privacy

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
    serializer_class = serializers.ReplaySerializer

    serializer_action_classes = {
        'list': serializers.ReplaySerializer,
        'create': serializers.ReplayCreateSerializer,
    }

    def get_serializer_class(self):
        """
        Look for serializer class in self.serializer_action_classes, which
        should be a dict mapping action name (key) to serializer class (value),
        i.e.:

        class MyViewSet(MultiSerializerViewSetMixin, ViewSet):
            serializer_class = serializers.MyDefaultSerializer
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

    def get_object(self):
        queryset = self.get_queryset()
        queryset = self.filter_queryset(queryset)
        filters = {}

        if 'replay_id' in self.kwargs:
            filters['replay_id'] = self.kwargs['replay_id']
        elif 'pk' in self.kwargs:
            filters['pk'] = self.kwargs['pk']

        return get_object_or_404(queryset, **filters)

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)

        # Add the replay to the netstream processing queue.
        process_netstream.apply_async([instance.pk], queue=instance.queue_priority)


class MapViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all maps in the system.
    """

    queryset = Map.objects.all()
    serializer_class = serializers.MapSerializer


class SeasonViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all seasons in the system.
    """

    queryset = Season.objects.all()
    serializer_class = serializers.SeasonSerializer


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all players in all games. These values are not unique.
    """

    queryset = Player.objects.all()
    serializer_class = serializers.PlayerSerializer


class GoalViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all goals in all games.
    """

    queryset = Goal.objects.all()
    serializer_class = serializers.GoalSerializer


class ComponentViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all of the car bodies available in-game.
    """

    queryset = Component.objects.all()
    serializer_class = serializers.ComponentSerializer


class LimitedPageNumberPagination(PageNumberPagination):
    page_size = 10


class ReplayPackViewSet(viewsets.ReadOnlyModelViewSet):

    """
    Returns a list of all of the car bodies available in-game.
    """

    queryset = ReplayPack.objects.all()
    serializer_class = serializers.ReplayPackSerializer
    pagination_class = LimitedPageNumberPagination


class LatestUserReplay(views.APIView):
    serializer_class = serializers.ReplaySerializer

    def get_serializer_context(self):
        user = get_object_or_404(User, pk=self.kwargs['user_id'])

        try:
            return Replay.objects.filter(
                user=user,
            ).order_by('-pk')[0]
        except IndexError:
            pass

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.get_serializer_context(), context={
            'request': request,
        })
        return Response(serializer.data)
