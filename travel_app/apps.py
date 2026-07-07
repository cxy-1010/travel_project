from django.apps import AppConfig


class TravelAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'travel_app'

    def ready(self):
        import travel_app.signals  # noqa: F401
