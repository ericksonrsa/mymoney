import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=140)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("due_date", models.DateField(null=True, blank=True)),
                ("status", models.CharField(choices=[("OPEN", "Em aberto"), ("PAID", "Paga"), ("CANCELLED", "Cancelada")], default="OPEN", max_length=12)),
                ("notes", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="finance_invoices", to=settings.AUTH_USER_MODEL)),
                ("transactions", models.ManyToManyField(blank=True, related_name="invoices", to="finance.transaction")),
            ],
            options={"ordering": ["-period_end", "title"]},
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["user", "status", "due_date"], name="fin_invoice_user_status_idx"),
        ),
    ]
