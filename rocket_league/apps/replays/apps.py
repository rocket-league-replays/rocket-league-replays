from django.apps import AppConfig


class ReplaysConfig(AppConfig):
    name = 'rocket_league.apps.replays'

    def ready(self):
        from . import signals
