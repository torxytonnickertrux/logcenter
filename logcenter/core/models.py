from django.db import models

class LogEntry(models.Model):
    TYPE_ACCESS = "access"
    TYPE_ERROR = "error"
    TYPE_SERVER = "server"
    TYPE_CHOICES = [
        (TYPE_ACCESS, "access"),
        (TYPE_ERROR, "error"),
        (TYPE_SERVER, "server"),
    ]
    LEVEL_INFO = "INFO"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"
    LEVEL_CRITICAL = "CRITICAL"
    LEVEL_CHOICES = [
        (LEVEL_INFO, "INFO"),
        (LEVEL_WARNING, "WARNING"),
        (LEVEL_ERROR, "ERROR"),
        (LEVEL_CRITICAL, "CRITICAL"),
    ]
    host = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    message = models.TextField()
    hash = models.CharField(max_length=128, unique=True)
    timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=["host"]),
            models.Index(fields=["type"]),
            models.Index(fields=["level"]),
            models.Index(fields=["received_at"]),
        ]

