from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'DeepFake Shield Core'

    def ready(self):
        """Ensure media directories exist on startup."""
        import os
        from django.conf import settings
        dirs = [
            settings.MEDIA_ROOT / 'uploads',
            settings.MEDIA_ROOT / 'processed',
            settings.MEDIA_ROOT / 'reports',
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)