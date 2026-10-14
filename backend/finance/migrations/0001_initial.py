import uuid
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MinValueValidator


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Account",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("institution", models.CharField(blank=True, max_length=120)),
                ("account_type", models.CharField(choices=[("CHECKING", "Conta corrente"), ("SAVINGS", "Poupança"), ("CREDIT_CARD", "Cartão de crédito"), ("CASH", "Dinheiro"), ("INVESTMENT", "Investimento"), ("OTHER", "Outro")], default="CHECKING", max_length=20)),
                ("opening_balance", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=14)),
                ("color", models.CharField(blank=True, max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="accounts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("category_type", models.CharField(choices=[("INCOME", "Receita"), ("EXPENSE", "Despesa")], max_length=10)),
                ("icon", models.CharField(blank=True, max_length=50)),
                ("color", models.CharField(blank=True, max_length=20)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="finance_categories", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["category_type", "name"]},
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("transaction_type", models.CharField(choices=[("INCOME", "Receita"), ("EXPENSE", "Despesa"), ("TRANSFER", "Transferência")], max_length=10)),
                ("description", models.CharField(max_length=200)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[MinValueValidator(Decimal("0.01"))])),
                ("transaction_date", models.DateField()),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="finance.account")),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="transactions", to="finance.category")),
                ("destination_account", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="incoming_transfers", to="finance.account")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="finance_transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-transaction_date", "-created_at"]},
        ),
        migrations.AddConstraint(model_name="account", constraint=models.UniqueConstraint(fields=("user", "name"), name="unique_account_name_per_user")),
        migrations.AddConstraint(model_name="category", constraint=models.UniqueConstraint(fields=("user", "name", "category_type"), name="unique_category_per_user_type")),
        migrations.AddIndex(model_name="transaction", index=models.Index(fields=["user", "transaction_date"], name="finance_tra_user_id_7b3c2b_idx")),
        migrations.AddIndex(model_name="transaction", index=models.Index(fields=["user", "transaction_type"], name="finance_tra_user_id_4f7c8e_idx")),
    ]
