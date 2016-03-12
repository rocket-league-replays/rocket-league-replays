from django.core.management import call_command
from django.contrib import admin
from django.db.models import Q

from .models import Replay, Player, Goal, Map, ReplayPack, Season


def reprocess_matches(modeladmin, request, queryset):
    call_command('reprocess_matches')
reprocess_matches.short_description = "Reprocess all matches"


def recalculate_average_rating(modeladmin, request, queryset):
    for obj in queryset:
        obj.average_rating = obj.calculate_average_rating()
        obj.save()


class PlayerInlineAdmin(admin.StackedInline):
    raw_id_fields = ['party_leader']

    readonly_fields = [field.name for field in Player._meta.fields]
    model = Player
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj):
        return False


class GoalInlineAdmin(admin.TabularInline):
    model = Goal
    fields = ['number', 'player', 'frame']
    readonly_fields = [field.name for field in Goal._meta.fields]
    extra = 0
    raw_id_fields = ['player']

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj):
        return False


class ReplayAdmin(admin.ModelAdmin):

    def has_heatmaps(self, obj):
        return obj.player_set.filter(
            Q(heatmap__isnull=True) | Q(heatmap=''),
        ).count() == 0
    has_heatmaps.boolean = True

    list_display = ['replay_id', 'user', 'map', 'team_sizes', 'average_rating', 'timestamp', 'has_heatmaps', 'processed', 'crashed_heatmap_parser']
    list_filter = ['user', 'season', 'team_sizes', 'average_rating', 'crashed_heatmap_parser']
    search_fields = ['replay_id']
    inlines = [PlayerInlineAdmin, GoalInlineAdmin]
    actions = [reprocess_matches, recalculate_average_rating]

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
