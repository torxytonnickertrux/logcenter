from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.db.models import Count
from django.conf import settings
from .models import LogEntry
import json
from urllib.request import Request, urlopen
from urllib.error import URLError

def send_alert(subject, body):
    if settings.EMAIL_HOST_USER:
        send_mail(subject, body, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER], fail_silently=True)
    url = getattr(settings, "WEBHOOK_URL", None)
    if url:
        try:
            payload = json.dumps({"subject": subject, "body": body}).encode("utf-8")
            req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
            urlopen(req, timeout=3)
        except URLError:
            pass

def evaluate_rules(entry):
    if entry.level == LogEntry.LEVEL_CRITICAL:
        send_alert("CRITICAL", f"{entry.host} {entry.message}")
        return
    if entry.level == LogEntry.LEVEL_ERROR:
        window_start = timezone.now() - timedelta(minutes=1)
        count = LogEntry.objects.filter(level=LogEntry.LEVEL_ERROR, received_at__gte=window_start).count()
        if count >= 5:
            send_alert("ERROR BURST", f"{count} errors in 1 minute")
