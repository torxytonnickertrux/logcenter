from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="System",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                ("slug", models.SlugField(unique=True, db_index=True)),
                ("description", models.TextField(blank=True)),
                ("environment", models.CharField(choices=[("dev", "dev"), ("staging", "staging"), ("prod", "prod")], default="dev", db_index=True, max_length=20)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name="LogIngestToken",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token_hash", models.CharField(max_length=128, unique=True)),
                ("is_active", models.BooleanField(default=True, db_index=True)),
                ("expires_at", models.DateTimeField(blank=True, null=True, db_index=True)),
                ("last_used_at", models.DateTimeField(blank=True, null=True, db_index=True)),
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("system", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="tokens", to="core.system", db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name="logentry",
            name="system",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="logs", to="core.system", db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="logentry",
            name="context",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="logentry",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, db_index=True, null=True),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=models.Index(fields=["system", "created_at"], name="core_log_sys_created_idx"),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=models.Index(fields=["system", "level"], name="core_log_sys_level_idx"),
        ),
        migrations.AddIndex(
            model_name="logentry",
            index=models.Index(fields=["system", "type"], name="core_log_sys_type_idx"),
        ),
    ]
