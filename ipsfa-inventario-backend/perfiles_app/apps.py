from django.apps import AppConfig


class PerfilesAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'perfiles_app'

    def ready(self):
        import perfiles_app.signals
