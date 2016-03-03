from django.apps import AppConfig

from validate_on_save import validate_models_on_save


class ReplaysConfig(AppConfig):
    name = 'rocket_league.apps.replays'

    def ready(self):
        from . import signals

        validate_models_on_save('replays')
