from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.utils.dateparse import parse_datetime
from django.utils.timezone import now
from django.views.generic import DetailView, TemplateView, UpdateView

from .forms import UserSettingsForm, PatreonSettingsForm
from .models import SteamCache
from ..replays.models import Replay

from braces.views import LoginRequiredMixin
import requests
from social.backends.steam import USER_INFO
from social.apps.django_app.default.models import UserSocialAuth
import xml.etree.ElementTree as ET


class UserSettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/user_settings.html'
    model = User
    form_class = UserSettingsForm
    success_message = "Your settings were successfully updated."

    def get_success_url(self):
        return reverse('users:settings')

    def get_object(self):
        return self.request.user


class PatreonSettingsView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    template_name = 'users/patreon_settings.html'
    model = User
    form_class = PatreonSettingsForm
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


class SteamView(TemplateView):
    template_name = 'users/steam_profile.html'

    def get(self, request, *args, **kwargs):
        if not kwargs['steam_id'].isnumeric():
            # Try to get the 64 bit ID for a user.
            try:
                data = requests.get('http://steamcommunity.com/id/{}/?xml=1'.format(
                    kwargs['steam_id']
                ))

                xml = ET.fromstring(data.text)

                kwargs['steam_id'] = xml.findall('steamID64')[0].text
                return redirect('users:steam', steam_id=kwargs['steam_id'])
            except Exception as e:
                raise Http404(e)

        return super(SteamView, self).get(request, *args, **kwargs)

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
            context['steam_info'] = None

            # Do we have a cache object for this already?
            try:
                cache = SteamCache.objects.filter(
                    uid=kwargs['steam_id']
                )

                if cache.count() > 0:
                    for cache_item in cache[1:]:
                        cache_item.delete()

                    cache = cache[0]

                    # Have we updated this profile recently?
                    if 'last_updated' in cache.extra_data:
                        # Parse the last updated date.
                        last_date = parse_datetime(cache.extra_data['last_updated'])

                        seconds_ago = (now() - last_date).seconds

                        # 3600  seconds = 1 hour
                        # 21600 seconds = 6 hours
                        if seconds_ago < 21600:
                            context['steam_info'] = cache.extra_data['player']

            except SteamCache.DoesNotExist:
                pass

            try:
                if not context['steam_info']:
                    player = requests.get(USER_INFO, params={
                        'key': settings.SOCIAL_AUTH_STEAM_API_KEY,
                        'steamids': kwargs['steam_id'],
                    }).json()

                    if len(player['response']['players']) > 0:
                        context['steam_info'] = player['response']['players'][0]

                        # Store this data in a SteamCache object.
                        cache_obj, _ = SteamCache.objects.get_or_create(
                            uid=kwargs['steam_id']
                        )
                        cache_obj.extra_data = {
                            'player': context['steam_info'],
                            'last_updated': now().isoformat(),
                        }
                        cache_obj.save()
            except:
                pass

        context['appears_in'] = Replay.objects.filter(
            show_leaderboard=True,
            player__platform='OnlinePlatform_Steam',
            player__online_id=kwargs['steam_id'],
        ).distinct()

        if not context.get('steam_info', None):
            context['steam_info'] = {
                'steamid': kwargs['steam_id'],
            }

        return context
