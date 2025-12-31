from django.contrib import admin
from django.utils.html import format_html
from django.utils.crypto import get_random_string
from django.contrib import messages
from hashlib import sha256
from .models import LogEntry, System, LogIngestToken

@admin.register(System)
class SystemAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "environment", "is_active", "created_at", "logs_count")
    list_filter = ("environment", "is_active", "created_at")
    search_fields = ("name", "slug", "description")
    actions = ["generate_token"]

    def logs_count(self, obj):
        return obj.logs.count()

    def generate_token(self, request, queryset):
        for system in queryset:
            plaintext = get_random_string(40)
            token_hash = sha256(plaintext.encode("utf-8")).hexdigest()
            LogIngestToken.objects.create(system=system, token_hash=token_hash, is_active=True)
            messages.success(request, f"Token para {system.slug}: {plaintext}")
    generate_token.short_description = "Gerar novo token (exibido uma vez)"

@admin.register(LogIngestToken)
class LogIngestTokenAdmin(admin.ModelAdmin):
    list_display = ("system", "is_active", "expires_at", "last_used_at", "created_at")
    list_filter = ("is_active", "system", "expires_at", "created_at")
    search_fields = ("system__name",)
    actions = ["revoke_tokens"]

    def revoke_tokens(self, request, queryset):
        updated = queryset.update(is_active=False)
        messages.success(request, f"{updated} token(s) revogado(s)")
    revoke_tokens.short_description = "Revogar tokens selecionados"

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
