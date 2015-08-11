from django.apps import AppConfig

import validate_on_save


class ReplaysConfig(AppConfig):
    name = 'rocket_league.apps.replays'

    def ready(self):
        import signals

        validate_on_save.validate_models_on_save('replays')
