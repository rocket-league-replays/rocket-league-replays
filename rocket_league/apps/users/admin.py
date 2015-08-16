from django.contrib import admin

from .models import LeagueRating


class LeagueRatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'duels', 'doubles', 'standard', 'timestamp']

admin.site.register(LeagueRating, LeagueRatingAdmin)
