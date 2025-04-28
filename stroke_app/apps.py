from django.apps import AppConfig

class StrokeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stroke_app'

    def ready(self):
        import stroke_app.signals