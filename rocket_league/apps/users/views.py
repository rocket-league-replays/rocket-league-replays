from django.views.generic import TemplateView


class ProfileView(TemplateView):
    template_name = 'users/user_profile.html'
