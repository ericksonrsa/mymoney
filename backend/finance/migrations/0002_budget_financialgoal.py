import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("finance", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("month", models.DateField(help_text="Primeiro dia do mês de referência")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("notes", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="budgets", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="finance_budgets", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-month", "category__name"]},
        ),
        migrations.CreateModel(
            name="FinancialGoal",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0.01"))])),
                ("current_amount", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=14, validators=[django.core.validators.MinValueValidator(Decimal("0"))])),
                ("target_date", models.DateField(blank=True, null=True)),
                ("notes", models.CharField(blank=True, max_length=200)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="financial_goals", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["is_active", "target_date", "name"]},
        ),
        migrations.AddConstraint(model_name="budget", constraint=models.UniqueConstraint(fields=("user", "category", "month"), name="unique_budget_per_category_month")),
        migrations.AddConstraint(model_name="financialgoal", constraint=models.UniqueConstraint(fields=("user", "name"), name="unique_goal_name_per_user")),
        migrations.AddIndex(model_name="budget", index=models.Index(fields=["user", "month"], name="finance_bud_user_id_8b7a4a_idx")),
    ]
