from django.contrib import admin

from .models import LeagueRating


class LeagueRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'duels', 'doubles', 'solo_standard', 'standard', 'timestamp']

admin.site.register(LeagueRating, LeagueRatingAdmin)
