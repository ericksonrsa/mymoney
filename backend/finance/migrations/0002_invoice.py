import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Budget",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("month", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[MinValueValidator(Decimal("0.01"))])),
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
                ("target_amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[MinValueValidator(Decimal("0.01"))])),
                ("current_amount", models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=14, validators=[MinValueValidator(Decimal("0"))])),
                ("target_date", models.DateField(blank=True, null=True)),
                ("notes", models.CharField(blank=True, max_length=200)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="financial_goals", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["is_active", "target_date", "name"]},
        ),
        migrations.CreateModel(
            name="RecurringTransaction",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("transaction_type", models.CharField(choices=[("INCOME", "Receita"), ("EXPENSE", "Despesa"), ("TRANSFER", "Transferência")], max_length=10)),
                ("description", models.CharField(max_length=200)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14, validators=[MinValueValidator(Decimal("0.01"))])),
                ("frequency", models.CharField(choices=[("WEEKLY", "Semanal"), ("MONTHLY", "Mensal"), ("YEARLY", "Anual")], max_length=10)),
                ("next_run", models.DateField()),
                ("end_date", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("notes", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="recurring_transactions", to="finance.account")),
                ("category", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="recurring_transactions", to="finance.category")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="recurring_transactions", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["next_run", "description"]},
        ),
        migrations.CreateModel(
            name="ImportBatch",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("filename", models.CharField(max_length=255)),
                ("status", models.CharField(choices=[("PREVIEW", "Pré-visualização"), ("IMPORTED", "Importado"), ("CANCELLED", "Cancelado")], default="PREVIEW", max_length=10)),
                ("total_rows", models.PositiveIntegerField(default=0)),
                ("imported_rows", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("account", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="import_batches", to="finance.account")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="import_batches", to=settings.AUTH_USER_MODEL)),
            ],
        ),
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
        migrations.CreateModel(
            name="Invoice",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=140)),
                ("period_start", models.DateField()),
                ("period_end", models.DateField()),
                ("due_date", models.DateField(blank=True, null=True)),
                ("status", models.CharField(choices=[("OPEN", "Em aberto"), ("PAID", "Paga"), ("CANCELLED", "Cancelada")], default="OPEN", max_length=12)),
                ("notes", models.CharField(blank=True, max_length=300)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("transactions", models.ManyToManyField(blank=True, related_name="invoices", to="finance.transaction")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="finance_invoices", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-period_end", "title"]},
        ),
        migrations.CreateModel(
            name="ImportRow",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transaction_date", models.DateField()),
                ("description", models.CharField(max_length=200)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=14)),
                ("transaction_type", models.CharField(choices=[("INCOME", "Receita"), ("EXPENSE", "Despesa")], max_length=10)),
                ("fingerprint", models.CharField(max_length=64)),
                ("status", models.CharField(default="PENDING", max_length=12)),
                ("error", models.CharField(blank=True, max_length=255)),
                ("batch", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rows", to="finance.importbatch")),
                ("transaction", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="import_row", to="finance.transaction")),
            ],
        ),
        migrations.AddConstraint(
            model_name="budget",
            constraint=models.UniqueConstraint(fields=("user", "category", "month"), name="unique_budget_per_category_month"),
        ),
        migrations.AddConstraint(
            model_name="financialgoal",
            constraint=models.UniqueConstraint(fields=("user", "name"), name="unique_goal_name_per_user"),
        ),
        migrations.AddIndex(
            model_name="budget",
            index=models.Index(fields=["user", "month"], name="finance_bud_user_id_5f8b32_idx"),
        ),
        migrations.AddIndex(
            model_name="recurringtransaction",
            index=models.Index(fields=["user", "next_run", "is_active"], name="finance_rec_user_id_1f5c42_idx"),
        ),
        migrations.AddConstraint(
            model_name="importrow",
            constraint=models.UniqueConstraint(fields=("batch", "fingerprint"), name="unique_import_row_fingerprint"),
        ),
        migrations.AddIndex(
            model_name="importrow",
            index=models.Index(fields=["batch", "fingerprint"], name="finance_imp_batch_i_6a42ab_idx"),
        ),
        migrations.AddIndex(
            model_name="categorizationrule",
            index=models.Index(fields=["user", "is_active", "priority"], name="finance_cat_user_id_8a34e1_idx"),
        ),
        migrations.AddConstraint(
            model_name="categorizationrule",
            constraint=models.UniqueConstraint(fields=("user", "name"), name="unique_categorization_rule_name"),
        ),
        migrations.AddConstraint(
            model_name="notification",
            constraint=models.UniqueConstraint(fields=("user", "dedupe_key"), name="unique_notification_dedupe_per_user"),
        ),
        migrations.AddIndex(
            model_name="notification",
            index=models.Index(fields=["user", "is_read", "-created_at"], name="fin_notif_user_read_idx"),
        ),
        migrations.AddIndex(
            model_name="invoice",
            index=models.Index(fields=["user", "status", "due_date"], name="fin_invoice_user_status_idx"),
        ),
    ]
