from django.test import TestCase
from django.utils import timezone
from logcenter.core.services import ingest, filter_logs, compute_level
from logcenter.core.models import System, LogEntry

class ServiceTests(TestCase):
    def setUp(self):
        self.system = System.objects.create(name="S", slug="s", environment="dev", is_active=True)

    def test_compute_level_override(self):
        lvl = compute_level("error", "ok", provided_level=LogEntry.LEVEL_INFO)
        self.assertEqual(lvl, LogEntry.LEVEL_INFO)

    def test_ingest_and_filter(self):
        p = {
            "host": "h",
            "type": "error",
            "message": "m",
            "hash": "z1",
            "timestamp": timezone.now().timestamp(),
            "context": {"k": "v"},
            "level": LogEntry.LEVEL_ERROR,
        }
        r, obj = ingest(self.system, p)
        self.assertEqual(r, "ok")
        self.assertEqual(obj.system_id, self.system.id)
        self.assertEqual(obj.context.get("k"), "v")
        qs = filter_logs(self.system, {"limit": "10"})
        self.assertEqual(qs.count(), 1)
