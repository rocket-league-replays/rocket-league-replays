from django.views.generic import ListView, DetailView, CreateView
from django.db.models import Q

from .forms import ReplayUploadForm
from .models import Replay


class ReplayListView(ListView):
    model = Replay

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
