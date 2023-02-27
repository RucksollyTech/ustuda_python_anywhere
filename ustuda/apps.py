from django.apps import AppConfig


class UstudaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ustuda'

    def ready(self):
        import ustuda.signals