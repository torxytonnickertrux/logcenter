from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "logcenter.core"

    def ready(self):
        token = os.environ.get("LOG_INGEST_TOKEN")
        if not token:
            return
        try:
            from hashlib import sha256
            from django.db.utils import OperationalError, ProgrammingError
            from .models import System, LogIngestToken
            sys, _ = System.objects.get_or_create(
                slug="default",
                defaults={"name": "Default", "environment": System.ENV_DEV, "is_active": True},
            )
            token_hash = sha256(token.encode("utf-8")).hexdigest()
            if not LogIngestToken.objects.filter(token_hash=token_hash).exists():
                LogIngestToken.objects.create(system=sys, token_hash=token_hash, is_active=True)
        except (OperationalError, ProgrammingError):
            # Database not ready (migrations not applied)
            return
