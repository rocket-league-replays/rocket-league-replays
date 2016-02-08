from django.core.management import call_command
from django.contrib import admin

from .models import Replay, Player, Goal, Map, ReplayPack, Season


def reprocess_matches(modeladmin, request, queryset):
    call_command('reprocess_matches')
reprocess_matches.short_description = "Reprocess all matches"


class PlayerInlineAdmin(admin.StackedInline):
    model = Player
    extra = 0


class GoalInlineAdmin(admin.StackedInline):
    model = Goal
    extra = 0
    raw_id_fields = ['player']


class ReplayAdmin(admin.ModelAdmin):
    list_display = ['replay_id', 'user', 'map', 'server_name', 'timestamp', 'processed']
    inlines = [PlayerInlineAdmin, GoalInlineAdmin]
    actions = [reprocess_matches]

admin.site.register(Replay, ReplayAdmin)


class MapAdmin(admin.ModelAdmin):

    def replay_count(self, obj):
        return obj.replay_set.count()

    list_display = ['title', 'slug', 'replay_count']

admin.site.register(Map, MapAdmin)


class ReplayPackAdmin(admin.ModelAdmin):
    filter_horizontal = ['replays']

admin.site.register(ReplayPack, ReplayPackAdmin)

admin.site.register(Season)
