from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Category, Invoice, Transaction


class Sprint12InvoiceApiTests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="invoice-owner", password="StrongPass123!")
        self.other = User.objects.create_user(username="invoice-other", password="StrongPass123!")
        self.client.force_authenticate(self.user)
        self.account = Account.objects.create(user=self.user, name="Conta fatura")
        self.income = Category.objects.create(user=self.user, name="Créditos", category_type="INCOME")
        self.expense = Category.objects.create(user=self.user, name="Débitos", category_type="EXPENSE")
        self.credit = Transaction.objects.create(
            user=self.user, account=self.account, category=self.income,
            transaction_type="INCOME", description="Estorno", amount=Decimal("25.00"),
            transaction_date=date.today(),
        )
        self.debit = Transaction.objects.create(
            user=self.user, account=self.account, category=self.expense,
            transaction_type="EXPENSE", description="Compra", amount=Decimal("80.50"),
            transaction_date=date.today(),
        )

    def test_invoice_consolidates_credit_and_debit_totals(self):
        response = self.client.post(reverse("invoice-list-create"), {
            "title": "Fatura de teste",
            "period_start": date.today().replace(day=1).isoformat(),
            "period_end": date.today().isoformat(),
            "transactions": [str(self.credit.id), str(self.debit.id)],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Decimal(str(response.data["credit_total"])), Decimal("25.00"))
        self.assertEqual(Decimal(str(response.data["debit_total"])), Decimal("80.50"))
        self.assertEqual(Decimal(str(response.data["net_total"])), Decimal("55.50"))
        self.assertEqual(response.data["transaction_count"], 2)

    def test_invoice_cannot_include_another_users_transaction(self):
        other_account = Account.objects.create(user=self.other, name="Conta alheia")
        other_category = Category.objects.create(user=self.other, name="Despesa alheia", category_type="EXPENSE")
        other_transaction = Transaction.objects.create(
            user=self.other, account=other_account, category=other_category,
            transaction_type="EXPENSE", description="Privado", amount=Decimal("10.00"),
            transaction_date=date.today(),
        )
        response = self.client.post(reverse("invoice-list-create"), {
            "title": "Fatura inválida",
            "period_start": date.today().replace(day=1).isoformat(),
            "period_end": date.today().isoformat(),
            "transactions": [str(other_transaction.id)],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Invoice.objects.filter(user=self.user).count(), 0)

    def test_transaction_cannot_be_assigned_to_two_invoices(self):
        payload = {
            "title": "Primeira",
            "period_start": date.today().replace(day=1).isoformat(),
            "period_end": date.today().isoformat(),
            "transactions": [str(self.debit.id)],
        }
        first = self.client.post(reverse("invoice-list-create"), payload, format="json")
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        payload["title"] = "Segunda"
        second = self.client.post(reverse("invoice-list-create"), payload, format="json")
        self.assertEqual(second.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invoice_lists_are_isolated_and_require_authentication(self):
        Invoice.objects.create(
            user=self.other, title="Privada", period_start=date.today().replace(day=1),
            period_end=date.today(), status=Invoice.Status.OPEN,
        )
        response = self.client.get(reverse("invoice-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("invoice-list-create"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_period_end_must_not_precede_start(self):
        response = self.client.post(reverse("invoice-list-create"), {
            "title": "Período inválido",
            "period_start": date.today().isoformat(),
            "period_end": (date.today() - timedelta(days=1)).isoformat(),
            "transactions": [],
        }, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
