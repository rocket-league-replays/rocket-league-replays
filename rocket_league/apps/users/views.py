from django.views.generic import TemplateView

from braces.views import LoginRequiredMixin


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_profile.html'
