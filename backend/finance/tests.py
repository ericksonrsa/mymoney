from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Category, Transaction


class FinanceApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="owner", password="StrongPass123!")
        self.other = User.objects.create_user(username="other", password="StrongPass123!")
        self.client.force_authenticate(self.user)
        self.account = Account.objects.create(user=self.user, name="Nubank", opening_balance=Decimal("1000"))
        self.category = Category.objects.create(user=self.user, name="Alimentação", category_type="EXPENSE")

    def test_accounts_are_isolated_by_user(self):
        Account.objects.create(user=self.other, name="Other Bank")
        response = self.client.get(reverse("account-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Nubank")

    def test_create_expense_belongs_to_authenticated_user(self):
        response = self.client.post(reverse("transaction-list-create"), {
            "account": str(self.account.id), "category": str(self.category.id),
            "transaction_type": "EXPENSE", "description": "Mercado", "amount": "150.00",
            "transaction_date": str(date.today()),
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        transaction = Transaction.objects.get(description="Mercado")
        self.assertEqual(transaction.user, self.user)

    def test_cannot_use_another_users_account(self):
        other_account = Account.objects.create(user=self.other, name="Other")
        response = self.client.post(reverse("transaction-list-create"), {
            "account": str(other_account.id), "category": str(self.category.id),
            "transaction_type": "EXPENSE", "description": "Invalid", "amount": "10.00",
            "transaction_date": str(date.today()),
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_aggregates_user_data_only(self):
        Transaction.objects.create(user=self.user, account=self.account, category=self.category, transaction_type="EXPENSE", description="Food", amount=Decimal("100"), transaction_date=date.today())
        other_account = Account.objects.create(user=self.other, name="Other")
        Transaction.objects.create(user=self.other, account=other_account, transaction_type="INCOME", description="Other income", amount=Decimal("9999"), transaction_date=date.today())
        response = self.client.get(reverse("finance-dashboard"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["balance"], 900)
