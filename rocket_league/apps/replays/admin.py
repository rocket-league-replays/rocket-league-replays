from django.contrib import admin
from djcelery.models import TaskMeta

from .models import (Component, BoostData, Goal, Map, Player, Replay, ReplayPack,
                     Season)
from .tasks import process_netstream


def reprocess_matches(modeladmin, request, queryset):
    for replay in queryset:
        process_netstream.apply_async([replay.pk], queue=replay.queue_priority)


reprocess_matches.short_description = "Reprocess selected matches"


def recalculate_average_rating(modeladmin, request, queryset):
    for obj in queryset:
        obj.average_rating = obj.calculate_average_rating()
        obj.save()


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    model = Player
    raw_id_fields = ['replay', 'party_leader']

    list_display = ['player_name', 'replay', 'platform']
    list_filter = ['platform']
    search_fields = ['replay__id']


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


class BoostDataInlineAdmin(admin.TabularInline):
    model = BoostData
    raw_id_fields = ['replay', 'player']
    readonly_fields = [field.name for field in BoostData._meta.fields]
    extra = 0

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj):
        return False


@admin.register(Replay)
class ReplayAdmin(admin.ModelAdmin):

    def has_heatmaps(self, obj):
        return bool(obj.heatmap_json_file)
    has_heatmaps.boolean = True

    list_display = ['pk', 'user', 'map', 'team_sizes', 'average_rating', 'timestamp', 'has_heatmaps', 'processed', 'crashed_heatmap_parser']
    list_filter = ['user', 'season', 'team_sizes', 'average_rating', 'processed', 'crashed_heatmap_parser']
    search_fields = ['replay_id']
    # inlines = [PlayerInlineAdmin, GoalInlineAdmin, BoostDataInlineAdmin]
    actions = [reprocess_matches, recalculate_average_rating]


@admin.register(Map)
class MapAdmin(admin.ModelAdmin):

    def replay_count(self, obj):
        return obj.replay_set.count()

    list_display = ['title', 'slug', 'replay_count']


@admin.register(ReplayPack)
class ReplayPackAdmin(admin.ModelAdmin):
    raw_id_fields = ['replays']


admin.site.register(Season)


@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['internal_id', 'name', 'type']
    list_filter = ['type']


@admin.register(TaskMeta)
class TaskMetaAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'status', 'date_done']
    list_filter = ['status']
    readonly_fields = ['result', 'meta']
