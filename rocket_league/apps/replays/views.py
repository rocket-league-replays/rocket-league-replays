from django.views.generic import ListView, DetailView

from .models import Replay


class ReplayListView(ListView):
    model = Replay


class ReplayDetailView(DetailView):
    model = Replay
