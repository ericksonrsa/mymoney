import uuid
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("finance", "0003_recurring_imports"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="CategorizationRule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("pattern", models.CharField(help_text="Texto literal a procurar, sem expressões regulares.", max_length=160)),
                ("match_field", models.CharField(choices=[("DESCRIPTION", "Descrição")], default="DESCRIPTION", max_length=12)),
                ("priority", models.PositiveSmallIntegerField(default=100, help_text="Número menor é aplicado primeiro.")),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="categorization_rules", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="categorization_rules", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["priority", "name"]},
        ),
        migrations.AddIndex(model_name="categorizationrule", index=models.Index(fields=["user", "is_active", "priority"], name="finance_cat_user_id_6a8b5c_idx")),
        migrations.AddConstraint(model_name="categorizationrule", constraint=models.UniqueConstraint(fields=("user", "name"), name="unique_categorization_rule_name")),
    ]
