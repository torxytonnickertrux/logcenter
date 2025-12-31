from django.test import TestCase, override_settings
from django.utils import timezone
from django.core import mail
from logcenter.core.models import System, LogEntry
from logcenter.core.alerts import evaluate_rules

class AlertTests(TestCase):
    def setUp(self):
        self.system = System.objects.create(name="S", slug="s", environment="dev", is_active=True)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", EMAIL_HOST_USER="noreply@example.com")
    def test_critical_alert_email(self):
        e = LogEntry.objects.create(system=self.system, host="h", type="error", message="c", hash="a1", timestamp=timezone.now(), level=LogEntry.LEVEL_CRITICAL, context={})
        evaluate_rules(e)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("CRITICAL", mail.outbox[0].subject)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend", EMAIL_HOST_USER="noreply@example.com")
    def test_burst_error_alert_email(self):
        for i in range(5):
            LogEntry.objects.create(system=self.system, host="h", type="error", message="e", hash=f"b{i}", timestamp=timezone.now(), level=LogEntry.LEVEL_ERROR, context={})
        e = LogEntry.objects.create(system=self.system, host="h", type="error", message="e", hash="bz", timestamp=timezone.now(), level=LogEntry.LEVEL_ERROR, context={})
        evaluate_rules(e)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ERROR BURST", mail.outbox[0].subject)
