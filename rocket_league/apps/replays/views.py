from django.db.models import Q
from django.views.generic import DetailView, CreateView

from .forms import ReplayUploadForm, ReplayFilter
from .models import Replay

from django_filters.views import FilterView


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
