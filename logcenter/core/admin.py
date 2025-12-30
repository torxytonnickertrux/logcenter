from django.contrib import admin
from django.utils.html import format_html
from .models import LogEntry

@admin.register(LogEntry)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ("host", "type", "colored_level", "received_at", "short_message", "hash")
    list_filter = ("host", "type", "level", "received_at")
    search_fields = ("host", "message", "hash")
    ordering = ("-received_at",)

    def short_message(self, obj):
        return (obj.message[:120] + "...") if len(obj.message) > 120 else obj.message

    def colored_level(self, obj):
        color = {
            LogEntry.LEVEL_INFO: "#3b82f6",
            LogEntry.LEVEL_WARNING: "#f59e0b",
            LogEntry.LEVEL_ERROR: "#ef4444",
            LogEntry.LEVEL_CRITICAL: "#7f1d1d",
        }[obj.level]
        return format_html('<span style="color:{};font-weight:600">{}</span>', color, obj.level)
    colored_level.admin_order_field = "level"
    colored_level.short_description = "Level"
