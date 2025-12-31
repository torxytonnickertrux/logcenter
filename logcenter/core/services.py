from datetime import datetime, timezone
from django.db import IntegrityError
from .models import LogEntry
from .alerts import evaluate_rules

def to_dt(ts):
    return datetime.fromtimestamp(float(ts), tz=timezone.utc)

def compute_level(log_type, message, provided_level=None):
    if provided_level:
        return provided_level
    m = (message or "").lower()
    if "critical" in m:
        return LogEntry.LEVEL_CRITICAL
    if log_type == LogEntry.TYPE_ERROR:
        return LogEntry.LEVEL_ERROR
    if "warn" in m or "warning" in m:
        return LogEntry.LEVEL_WARNING
    return LogEntry.LEVEL_INFO

def ingest(system, payload):
    host = payload["host"]
    log_type = payload["type"]
    message = payload["message"]
    hash_value = payload["hash"]
    ts = to_dt(payload["timestamp"])
    level = compute_level(log_type, message, payload.get("level"))
    context = payload.get("context") or {}
    try:
        obj = LogEntry.objects.create(
            system=system,
            host=host,
            type=log_type,
            message=message,
            hash=hash_value,
            timestamp=ts,
            level=level,
            context=context,
        )
        evaluate_rules(obj)
        return "ok", obj
    except IntegrityError:
        return "duplicate", None

def filter_logs(system, params):
    qs = LogEntry.objects.filter(system=system).order_by("-received_at")
    host = params.get("host")
    type_ = params.get("type")
    level = params.get("level")
    since = params.get("since")
    until = params.get("until")
    limit = params.get("limit")
    if host:
        qs = qs.filter(host=host)
    if type_:
        qs = qs.filter(type=type_)
    if level:
        qs = qs.filter(level=level)
    if since:
        qs = qs.filter(received_at__gte=to_dt(since))
    if until:
        qs = qs.filter(received_at__lte=to_dt(until))
    if limit:
        try:
            n = int(limit)
            qs = qs[:max(1, min(n, 1000))]
        except ValueError:
            qs = qs[:100]
    else:
        qs = qs[:100]
    return qs
