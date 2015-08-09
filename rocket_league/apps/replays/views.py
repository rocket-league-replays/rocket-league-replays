from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.views.generic import ListView, DeleteView, DetailView, CreateView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin

from .forms import ReplayUploadForm, ReplayFilter, ReplayPackForm, ReplayUpdateForm
from .models import Goal, Map, Player, Replay, ReplayPack
from .serializers import GoalSerializer, MapSerializer, PlayerSerializer, ReplaySerializer
from ...utils.forms import AjaxableResponseMixin

from braces.views import LoginRequiredMixin
from django_filters.views import FilterView
from rest_framework import viewsets

from zipfile import ZipFile
import re
import StringIO


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

    def get_success_url(self):
        return self.request.path


# Replay packs
class ReplayPackCreateView(LoginRequiredMixin, CreateView):
    model = ReplayPack
    form_class = ReplayPackForm
    template_name_suffix = '_create'

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


class ReplayPackDetailView(DetailView):
    model = ReplayPack


class ReplayPackListView(ListView):
    model = ReplayPack
    paginate_by = 20


class ReplayPackDeleteView(DeleteView):
    model = ReplayPack

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_object().user:
            raise PermissionDenied

        return super(ReplayPackDeleteView, self).dispatch(request, *args, **kwargs)


class ReplayPackDownloadView(SingleObjectMixin, View):
    model = ReplayPack

    def get(self, request, *args, **kwargs):
        obj = self.get_object()
        zip_filename = '{}.zip'.format(str(obj))
        zip_string = StringIO.StringIO()

        with ZipFile(zip_string, 'w') as f:
            for replay in obj.replays.all():
                filename = '{}.replay'.format(replay.replay_id)
                f.write(replay.file.path, filename)

            # Create a README file.
            readme = render_to_string('replays/readme.html', {
                'replaypack': obj,
            })

            f.writestr('README.txt', str(readme))
        f.close()

        # print zip_string.getvalue()

        response = HttpResponse(zip_string.getvalue(), content_type="application/x-zip-compressed")
        response['Content-Disposition'] = 'attachment; filename={}'.format(zip_filename)
        return response


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
