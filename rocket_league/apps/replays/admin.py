from django.core.management import call_command
from django.contrib import admin
from django.db.models import Q

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

    def has_heatmaps(self, obj):
        return obj.player_set.filter(
            Q(heatmap__isnull=True) | Q(heatmap=''),
        ).count() == 0
    has_heatmaps.boolean = True

    list_display = ['replay_id', 'user', 'map', 'server_name', 'timestamp', 'has_heatmaps', 'processed']
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
