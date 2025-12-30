from rest_framework import serializers
from .models import LogEntry

class IngestSerializer(serializers.Serializer):
    host = serializers.CharField()
    type = serializers.ChoiceField(choices=[("access", "access"), ("error", "error"), ("server", "server")])
    message = serializers.CharField()
    hash = serializers.CharField()
    timestamp = serializers.FloatField()

class LogEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LogEntry
        fields = ["id", "host", "type", "message", "hash", "timestamp", "received_at", "level"]

