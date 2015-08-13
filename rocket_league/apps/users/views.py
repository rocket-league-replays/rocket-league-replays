from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.views.generic import DetailView, UpdateView

from .forms import UserSettingsForm

from braces.views import LoginRequiredMixin
from registration import signals
from registration.views import RegistrationView as BaseRegistrationView


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


class RegistrationView(BaseRegistrationView):
    """
    A registration backend which implements the simplest possible
    workflow: a user supplies a username, email address and password
    (the bare minimum for a useful account), and is immediately signed
    up and logged in).
    """
    def register(self, **cleaned_data):
        username, password = (cleaned_data['username'], cleaned_data['password1'])
        User.objects.create_user(username, '', password)

        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        signals.user_registered.send(
            sender=self.__class__,
            user=new_user,
            request=self.request
        )
        return new_user

    def get_success_url(self, user):
        return '/'
