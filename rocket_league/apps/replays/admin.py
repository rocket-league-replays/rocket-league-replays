from django.contrib import admin

from .models import Replay, Player, Goal, Map, ReplayPack


class PlayerInlineAdmin(admin.StackedInline):
    model = Player
    extra = 0


class GoalInlineAdmin(admin.StackedInline):
    model = Goal
    extra = 0


class ReplayAdmin(admin.ModelAdmin):
    list_display = ['replay_id', 'user', 'map', 'server_name', 'timestamp', 'processed']
    inlines = [PlayerInlineAdmin, GoalInlineAdmin]

admin.site.register(Replay, ReplayAdmin)
admin.site.register(Map)


admin.site.register(ReplayPack)
