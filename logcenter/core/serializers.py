from rest_framework import serializers
from .models import LogEntry

class IngestSerializer(serializers.Serializer):
    host = serializers.CharField()
    type = serializers.ChoiceField(choices=[("access", "access"), ("error", "error"), ("server", "server")])
    level = serializers.ChoiceField(choices=[("INFO", "INFO"), ("WARNING", "WARNING"), ("ERROR", "ERROR"), ("CRITICAL", "CRITICAL")], required=False)
    message = serializers.CharField()
    hash = serializers.CharField()
    timestamp = serializers.FloatField()
    context = serializers.DictField(required=False)

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = ["id", "system_id", "host", "type", "message", "hash", "timestamp", "received_at", "level", "context", "created_at"]
