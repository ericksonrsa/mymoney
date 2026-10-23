import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Account(models.Model):
    class AccountType(models.TextChoices):
        CHECKING = "CHECKING", "Conta corrente"
        SAVINGS = "SAVINGS", "Poupança"
        CREDIT_CARD = "CREDIT_CARD", "Cartão de crédito"
        CASH = "CASH", "Dinheiro"
        INVESTMENT = "INVESTMENT", "Investimento"
        OTHER = "OTHER", "Outro"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="accounts")
    name = models.CharField(max_length=120); institution = models.CharField(max_length=120, blank=True)
    account_type = models.CharField(max_length=20, choices=AccountType.choices, default=AccountType.CHECKING)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0")); color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["user", "name"], name="unique_account_name_per_user")]
    def __str__(self): return self.name

class Category(models.Model):
    class CategoryType(models.TextChoices): INCOME = "INCOME", "Receita"; EXPENSE = "EXPENSE", "Despesa"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_categories")
    name = models.CharField(max_length=100); category_type = models.CharField(max_length=10, choices=CategoryType.choices)
    icon = models.CharField(max_length=50, blank=True); color = models.CharField(max_length=20, blank=True); is_active = models.BooleanField(default=True); created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["category_type", "name"]
        constraints = [models.UniqueConstraint(fields=["user", "name", "category_type"], name="unique_category_per_user_type")]
    def __str__(self): return self.name

class Transaction(models.Model):
    class TransactionType(models.TextChoices): INCOME = "INCOME", "Receita"; EXPENSE = "EXPENSE", "Despesa"; TRANSFER = "TRANSFER", "Transferência"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_transactions")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions")
    destination_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="incoming_transfers", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    description = models.CharField(max_length=200); amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]); transaction_date = models.DateField(); notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        indexes = [models.Index(fields=["user", "transaction_date"]), models.Index(fields=["user", "transaction_type"])]
    def __str__(self): return f"{self.description} - {self.amount}"

class Budget(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False); user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_budgets"); category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="budgets"); month = models.DateField(); amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]); notes = models.CharField(max_length=200, blank=True); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["-month", "category__name"]; constraints = [models.UniqueConstraint(fields=["user", "category", "month"], name="unique_budget_per_category_month")]; indexes = [models.Index(fields=["user", "month"])]

class FinancialGoal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False); user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="financial_goals"); name = models.CharField(max_length=120); target_amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01") )]); current_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"), validators=[MinValueValidator(Decimal("0"))]); target_date = models.DateField(null=True, blank=True); notes = models.CharField(max_length=200, blank=True); is_active = models.BooleanField(default=True); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ["is_active", "target_date", "name"]; constraints = [models.UniqueConstraint(fields=["user", "name"], name="unique_goal_name_per_user")]

class RecurringTransaction(models.Model):
    class Frequency(models.TextChoices): WEEKLY="WEEKLY","Semanal"; MONTHLY="MONTHLY","Mensal"; YEARLY="YEARLY","Anual"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False); user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="recurring_transactions"); account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="recurring_transactions"); category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True, blank=True, related_name="recurring_transactions"); transaction_type = models.CharField(max_length=10, choices=Transaction.TransactionType.choices); description = models.CharField(max_length=200); amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))]); frequency = models.CharField(max_length=10, choices=Frequency.choices); next_run = models.DateField(); end_date = models.DateField(null=True, blank=True); is_active = models.BooleanField(default=True); notes = models.CharField(max_length=200, blank=True); created_at = models.DateTimeField(auto_now_add=True); updated_at = models.DateTimeField(auto_now=True)
    class Meta: ordering=["next_run","description"]; indexes=[models.Index(fields=["user","next_run","is_active"])]

class ImportBatch(models.Model):
    class Status(models.TextChoices): PREVIEW="PREVIEW","Pré-visualização"; IMPORTED="IMPORTED","Importado"; CANCELLED="CANCELLED","Cancelado"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False); user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="import_batches"); account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="import_batches"); filename = models.CharField(max_length=255); status = models.CharField(max_length=10, choices=Status.choices, default=Status.PREVIEW); total_rows = models.PositiveIntegerField(default=0); imported_rows = models.PositiveIntegerField(default=0); created_at = models.DateTimeField(auto_now_add=True)

class ImportRow(models.Model):
    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="rows"); transaction_date = models.DateField(); description = models.CharField(max_length=200); amount = models.DecimalField(max_digits=14, decimal_places=2); transaction_type = models.CharField(max_length=10, choices=[("INCOME","Receita"),("EXPENSE","Despesa")]); fingerprint = models.CharField(max_length=64); status = models.CharField(max_length=12, default="PENDING"); transaction = models.OneToOneField(Transaction, on_delete=models.SET_NULL, null=True, blank=True, related_name="import_row"); error = models.CharField(max_length=255, blank=True)
    class Meta: constraints=[models.UniqueConstraint(fields=["batch","fingerprint"],name="unique_import_row_fingerprint")]; indexes=[models.Index(fields=["batch","fingerprint"])]
