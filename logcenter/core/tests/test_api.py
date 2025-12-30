import os
from django.test import TestCase
from rest_framework.test import APIClient
from django.utils import timezone
from logcenter.core.models import LogEntry

class APITests(TestCase):
    def setUp(self):
        os.environ["LOG_INGEST_TOKEN"] = "test-token"
        self.client = APIClient()
        self.valid = {
            "host": "vilksonvtch.pythonanywhere.com",
            "type": "error",
            "message": "something failed",
            "hash": "abc123",
            "timestamp": timezone.now().timestamp(),
        }

    def auth(self):
        return {"HTTP_AUTHORIZATION": "Bearer test-token"}

    def test_invalid_token(self):
        r = self.client.post("/api/ingest/", self.valid, format="json")
        self.assertEqual(r.status_code, 401)

    def test_payload_invalid(self):
        payload = dict(self.valid)
        del payload["message"]
        r = self.client.post("/api/ingest/", payload, format="json", **self.auth())
        self.assertEqual(r.status_code, 400)

    def test_duplicate(self):
        r1 = self.client.post("/api/ingest/", self.valid, format="json", **self.auth())
        self.assertEqual(r1.status_code, 200)
        r2 = self.client.post("/api/ingest/", self.valid, format="json", **self.auth())
        self.assertEqual(r2.status_code, 200)
        self.assertEqual(r2.json()["status"], "duplicate")

    def test_filters(self):
        for i in range(3):
            p = dict(self.valid)
            p["hash"] = f"h{i}"
            self.client.post("/api/ingest/", p, format="json", **self.auth())
        r = self.client.get("/api/logs/?type=error&limit=2", **self.auth())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()), 2)

    def test_alert_error_burst(self):
        for i in range(5):
            p = dict(self.valid)
            p["hash"] = f"x{i}"
            self.client.post("/api/ingest/", p, format="json", **self.auth())
        self.assertEqual(LogEntry.objects.count(), 5)
