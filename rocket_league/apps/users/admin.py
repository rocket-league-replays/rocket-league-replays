from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import LeagueRating, Profile


class LeagueRatingAdmin(admin.ModelAdmin):
    list_display = ['platform', 'online_id', 'timestamp']
    search_fields = ['online_id']


admin.site.register(LeagueRating, LeagueRatingAdmin)


class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(UserAdmin):

    def has_steam(self, obj):
        return bool(obj.social_auth.filter(provider='steam').count())
    has_steam.boolean = True

    list_display = ['username', 'token', 'has_steam', 'is_staff']
    inlines = [ProfileInline]


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
