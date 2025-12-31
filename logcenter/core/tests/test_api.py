import os
from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from hashlib import sha256
from logcenter.core.models import LogEntry, System, LogIngestToken

class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.system_a = System.objects.create(name="Loja A", slug="loja-a", environment="dev", is_active=True)
        self.system_b = System.objects.create(name="Loja B", slug="loja-b", environment="dev", is_active=True)
        self.token_a_plain = "test-token-a"
        self.token_b_plain = "test-token-b"
        LogIngestToken.objects.create(system=self.system_a, token_hash=sha256(self.token_a_plain.encode("utf-8")).hexdigest(), is_active=True)
        LogIngestToken.objects.create(system=self.system_b, token_hash=sha256(self.token_b_plain.encode("utf-8")).hexdigest(), is_active=True)
        self.valid = {
            "host": "vilksonvtch.pythonanywhere.com",
            "type": "error",
            "message": "something failed",
            "hash": "abc123",
            "timestamp": timezone.now().timestamp(),
            "context": {"path": "/index"},
        }

    def auth_a(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.token_a_plain}"}
    def auth_b(self):
        return {"HTTP_AUTHORIZATION": f"Bearer {self.token_b_plain}"}

    def test_invalid_token(self):
        r = self.client.post("/api/ingest/", self.valid, format="json")
        self.assertEqual(r.status_code, 401)

    def test_payload_invalid(self):
        payload = dict(self.valid)
        del payload["message"]
        r = self.client.post("/api/ingest/", payload, format="json", **self.auth_a())
        self.assertEqual(r.status_code, 400)

    def test_duplicate(self):
        r1 = self.client.post("/api/ingest/", self.valid, format="json", **self.auth_a())
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.post("/api/ingest/", self.valid, format="json", **self.auth_a())
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "duplicate")

    def test_filters(self):
        for i in range(3):
            p = dict(self.valid)
            p["hash"] = f"h{i}"
            self.client.post("/api/ingest/", p, format="json", **self.auth_a())
        r = self.client.get("/api/logs/?type=error&limit=2", **self.auth_a())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 2)

    def test_alert_error_burst(self):
        for i in range(5):
            p = dict(self.valid)
            p["hash"] = f"x{i}"
            self.client.post("/api/ingest/", p, format="json", **self.auth_a())
        self.assertEqual(LogEntry.objects.filter(system=self.system_a).count(), 5)

    def test_isolation_between_systems(self):
        p1 = dict(self.valid)
        p1["hash"] = "iso1"
        p2 = dict(self.valid)
        p2["hash"] = "iso2"
        self.client.post("/api/ingest/", p1, format="json", **self.auth_a())
        self.client.post("/api/ingest/", p2, format="json", **self.auth_b())
        ra = self.client.get("/api/logs/?limit=10", **self.auth_a())
        rb = self.client.get("/api/logs/?limit=10", **self.auth_b())
        self.assertEqual(len(ra.json()), 1)
        self.assertEqual(len(rb.json()), 1)

    def test_revoked_token(self):
        # revoke system A token
        tok = LogIngestToken.objects.get(token_hash=sha256(self.token_a_plain.encode("utf-8")).hexdigest())
        tok.is_active = False
        tok.save()
        r = self.client.post("/api/ingest/", self.valid, format="json", **self.auth_a())
        self.assertEqual(r.status_code, 401)
