from django.contrib.auth.models import User
from django.views.generic import DetailView, TemplateView

from braces.views import LoginRequiredMixin


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_profile.html'


class PublicProfileView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'users/user_public_profile.html'
