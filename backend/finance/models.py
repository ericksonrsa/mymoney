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
    name = models.CharField(max_length=120)
    institution = models.CharField(max_length=120, blank=True)
    account_type = models.CharField(max_length=20, choices=AccountType.choices, default=AccountType.CHECKING)
    opening_balance = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [models.UniqueConstraint(fields=["user", "name"], name="unique_account_name_per_user")]

    def __str__(self):
        return self.name


class Category(models.Model):
    class CategoryType(models.TextChoices):
        INCOME = "INCOME", "Receita"
        EXPENSE = "EXPENSE", "Despesa"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_categories")
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CategoryType.choices)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category_type", "name"]
        constraints = [models.UniqueConstraint(fields=["user", "name", "category_type"], name="unique_category_per_user_type")]

    def __str__(self):
        return self.name


class Transaction(models.Model):
    class TransactionType(models.TextChoices):
        INCOME = "INCOME", "Receita"
        EXPENSE = "EXPENSE", "Despesa"
        TRANSFER = "TRANSFER", "Transferência"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="finance_transactions")
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="transactions")
    destination_account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name="incoming_transfers", null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="transactions", null=True, blank=True)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0.01"))])
    transaction_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-transaction_date", "-created_at"]
        indexes = [models.Index(fields=["user", "transaction_date"]), models.Index(fields=["user", "transaction_type"])]

    def __str__(self):
        return f"{self.description} - {self.amount}"
