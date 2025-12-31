from django.db import models
from django.utils import timezone

class System(models.Model):
    ENV_DEV = "dev"
    ENV_STAGING = "staging"
    ENV_PROD = "prod"
    ENV_CHOICES = [
        (ENV_DEV, "dev"),
        (ENV_STAGING, "staging"),
        (ENV_PROD, "prod"),
    ]
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    environment = models.CharField(max_length=20, choices=ENV_CHOICES, default=ENV_DEV, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.name} ({self.environment})"

class LogIngestToken(models.Model):
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name="tokens", db_index=True)
    token_hash = models.CharField(max_length=128, unique=True)
    is_active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_used_at = models.DateTimeField(null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return self.system.is_active

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
    system = models.ForeignKey(System, on_delete=models.CASCADE, related_name="logs", db_index=True, null=True)
    host = models.CharField(max_length=255, db_index=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    message = models.TextField()
    hash = models.CharField(max_length=128, unique=True)
    timestamp = models.DateTimeField()
    received_at = models.DateTimeField(auto_now_add=True, db_index=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, db_index=True)
    context = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["system", "created_at"]),
            models.Index(fields=["system", "level"]),
            models.Index(fields=["system", "type"]),
            models.Index(fields=["host"]),
            models.Index(fields=["type"]),
            models.Index(fields=["level"]),
            models.Index(fields=["received_at"]),
        ]
