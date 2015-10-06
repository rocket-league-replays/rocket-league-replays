from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import LeagueRating


class LeagueRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'duels', 'doubles', 'solo_standard', 'standard', 'timestamp']

admin.site.register(LeagueRating, LeagueRatingAdmin)


class UserAdmin(UserAdmin):
    list_display = ['username', 'token', 'is_staff']

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
