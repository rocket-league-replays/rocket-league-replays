from django.views.generic import ListView, DetailView, CreateView

from .forms import ReplayUploadForm
from .models import Replay


class ReplayListView(ListView):
    model = Replay


class ReplayDetailView(DetailView):
    model = Replay


class ReplayCreateView(CreateView):
    model = Replay
    form_class = ReplayUploadForm
