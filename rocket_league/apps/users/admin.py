from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import LeagueRating


class LeagueRatingAdmin(admin.ModelAdmin):
    list_display = ['steamid', 'duels', 'doubles', 'solo_standard', 'standard', 'timestamp']
    search_fields = ['steamid']

admin.site.register(LeagueRating, LeagueRatingAdmin)


class UserAdmin(UserAdmin):

    def has_steam(self, obj):
        return bool(obj.social_auth.filter(provider='steam').count())
    has_steam.boolean = True

    list_display = ['username', 'token', 'has_steam', 'is_staff']

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
