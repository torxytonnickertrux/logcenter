from django.test import TestCase
from django.utils import timezone
from logcenter.core.models import System, LogIngestToken

class ModelTests(TestCase):
    def setUp(self):
        self.system = System.objects.create(name="S", slug="s", environment="dev", is_active=True)

    def test_token_validity(self):
        tok = LogIngestToken.objects.create(system=self.system, token_hash="h", is_active=True)
        self.assertTrue(tok.is_valid())
        self.system.is_active = False
        self.system.save()
        self.assertFalse(LogIngestToken.objects.get(id=tok.id).is_valid())

    def test_token_expired(self):
        tok = LogIngestToken.objects.create(system=self.system, token_hash="x", is_active=True, expires_at=timezone.now())
        tok.expires_at = timezone.now()
        tok.save()
        self.assertFalse(tok.is_valid())
