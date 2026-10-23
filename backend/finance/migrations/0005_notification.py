import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0004_categorizationrule"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("notification_type", models.CharField(max_length=32)),
                ("severity", models.CharField(choices=[("INFO", "Informativa"), ("WARNING", "Atenção"), ("CRITICAL", "Crítica")], default="INFO", max_length=10)),
                ("title", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("dedupe_key", models.CharField(max_length=200)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("is_read", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="finance_notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["is_read", "-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(fields=("user", "dedupe_key"), name="unique_notification_dedupe_per_user"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["user", "is_read", "-created_at"], name="fin_notif_user_read_idx"),
        ),
    ]
