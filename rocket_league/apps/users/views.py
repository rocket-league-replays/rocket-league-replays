from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, UpdateView

from .forms import UserSettingsForm

from braces.views import LoginRequiredMixin


class ProfileView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/user_profile.html'
    model = User
    form_class = UserSettingsForm
    success_message = "Your settings were successfully updated."

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return '{}#settings-tab'.format(
            reverse('users:profile')
        )


class PublicProfileView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'users/user_public_profile.html'
