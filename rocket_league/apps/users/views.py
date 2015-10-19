from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic import DetailView, TemplateView, UpdateView

from .forms import UserSettingsForm
from ..replays.models import Replay

from braces.views import LoginRequiredMixin
from registration import signals
from registration.views import RegistrationView as BaseRegistrationView
import requests
from social.backends.steam import USER_INFO
from social.apps.django_app.default.models import UserSocialAuth


class UserMixin(LoginRequiredMixin, DetailView):
    model = User

    def get_object(self):
        return self.request.user


class UserReplaysView(UserMixin):
    template_name = 'users/user_replays.html'


class UserReplayPacksView(UserMixin):
    template_name = 'users/user_replay_packs.html'


class UserDesktopApplicationView(UserMixin):
    template_name = 'users/user_desktop_application.html'


class UserRankTrackerView(UserMixin):
    template_name = 'users/user_rank_tracker.html'


class UserSettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/user_settings.html'
    model = User
    form_class = UserSettingsForm
    success_message = "Your settings were successfully updated."

    def get_success_url(self):
        return reverse('users:settings')

    def get_object(self):
        return self.request.user


class PublicProfileView(DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    template_name = 'users/user_public_profile.html'
    context_object_name = 'public_user'

    def get(self, request, *args, **kwargs):
        response = super(PublicProfileView, self).get(request, *args, **kwargs)

        if self.object.profile.has_steam_connected():
            return redirect('users:steam', steam_id=self.object.profile.steam_info()['steamid'])

        return response


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
        return settings.LOGIN_REDIRECT_URL


class SteamView(TemplateView):
    template_name = 'users/steam_profile.html'

    def get_context_data(self, **kwargs):
        context = super(SteamView, self).get_context_data(**kwargs)

        # Is this Steam ID associated with a user?
        try:
            social_obj = UserSocialAuth.objects.get(
                uid=kwargs['steam_id'],
            )
            context['steam_info'] = social_obj.extra_data['player']

            context['uploaded'] = social_obj.user.replay_set.all()
            context['has_user'] = True
        except UserSocialAuth.DoesNotExist:
            # Pull the profile data and pass it in.
            context['has_user'] = False

            # TODO: Store this data, rather than requesting it every time.
            try:
                player = requests.get(USER_INFO, params={
                    'key': settings.SOCIAL_AUTH_STEAM_API_KEY,
                    'steamids': kwargs['steam_id'],
                }).json()

                if len(player['response']['players']) > 0:
                    context['steam_info'] = player['response']['players'][0]
            except:
                pass

        context['appears_in'] = Replay.objects.filter(
            show_leaderboard=True,
            player__platform='OnlinePlatform_Steam',
            player__online_id=kwargs['steam_id'],
        )

        return context
