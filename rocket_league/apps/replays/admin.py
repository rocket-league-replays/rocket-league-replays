from django.core.management import call_command
from django.contrib import admin

from .models import Replay, Player, Goal, Map, ReplayPack


def reprocess_matches(modeladmin, request, queryset):
    call_command('reprocess_matches')
reprocess_matches.short_description = "Reprocess all matches"


class PlayerInlineAdmin(admin.StackedInline):
    model = Player
    extra = 0


class GoalInlineAdmin(admin.StackedInline):
    model = Goal
    extra = 0


class ReplayAdmin(admin.ModelAdmin):
    list_display = ['replay_id', 'user', 'map', 'server_name', 'timestamp', 'processed']
    inlines = [PlayerInlineAdmin, GoalInlineAdmin]
    actions = [reprocess_matches]

admin.site.register(Replay, ReplayAdmin)
admin.site.register(Map)


admin.site.register(ReplayPack)
