from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="LogEntry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("host", models.CharField(db_index=True, max_length=255)),
                ("type", models.CharField(choices=[("access", "access"), ("error", "error"), ("server", "server")], db_index=True, max_length=20)),
                ("message", models.TextField()),
                ("hash", models.CharField(max_length=128, unique=True)),
                ("timestamp", models.DateTimeField()),
                ("received_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("level", models.CharField(choices=[("INFO", "INFO"), ("WARNING", "WARNING"), ("ERROR", "ERROR"), ("CRITICAL", "CRITICAL")], db_index=True, max_length=20)),
            ],
            options={"indexes": [models.Index(fields=["host"], name="core_log_host_idx"), models.Index(fields=["type"], name="core_log_type_idx"), models.Index(fields=["level"], name="core_log_level_idx"), models.Index(fields=["received_at"], name="core_log_received_idx")]},
        ),
    ]

