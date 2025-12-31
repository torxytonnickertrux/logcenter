from hashlib import sha256
from types import SimpleNamespace
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed
from logcenter.core.authentication import BearerTokenAuthentication
from logcenter.core.models import System, LogIngestToken

class AuthTests(TestCase):
    def setUp(self):
        self.system = System.objects.create(name="S", slug="s", environment="dev", is_active=True)
        self.plain = "tok123"
        LogIngestToken.objects.create(system=self.system, token_hash=sha256(self.plain.encode("utf-8")).hexdigest(), is_active=True)

    def test_authenticate_success(self):
        req = SimpleNamespace(headers={"Authorization": f"Bearer {self.plain}"})
        user_token = BearerTokenAuthentication().authenticate(req)
        self.assertIsNotNone(user_token)
        self.assertTrue(hasattr(req, "system"))
        self.assertEqual(req.system.id, self.system.id)

    def test_authenticate_invalid(self):
        req = SimpleNamespace(headers={"Authorization": "Bearer wrong"})
        with self.assertRaises(AuthenticationFailed):
            BearerTokenAuthentication().authenticate(req)
