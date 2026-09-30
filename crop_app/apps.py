from django.apps import AppConfig
from django.db.models.signals import post_migrate


class CropAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'crop_app'

    def ready(self):
        def auto_seed_if_empty(sender, **kwargs):
            try:
                from .models import CropInformation
                if CropInformation.objects.count() == 0:
                    import seed_db
                    seed_db.seed_crops()
            except Exception:
                pass

        post_migrate.connect(auto_seed_if_empty, sender=self)
