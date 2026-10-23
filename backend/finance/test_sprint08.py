from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Account, Budget, Category, FinancialGoal, Notification, RecurringTransaction, Transaction


class Sprint08ApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="sprint08-user", password="test-password-123")
        self.other = get_user_model().objects.create_user(username="sprint08-other", password="test-password-123")
        self.client.force_authenticate(self.user)
        self.account = Account.objects.create(user=self.user, name="Conta principal")
        self.expense_category = Category.objects.create(user=self.user, name="Moradia", category_type="EXPENSE")
        self.income_category = Category.objects.create(user=self.user, name="Salário", category_type="INCOME")

    def test_insights_returns_monthly_totals_and_categories(self):
        today = date.today()
        start = today.replace(day=1)
        Transaction.objects.create(user=self.user, account=self.account, category=self.income_category,
            transaction_type="INCOME", description="Salário", amount=Decimal("5000.00"), transaction_date=start)
        Transaction.objects.create(user=self.user, account=self.account, category=self.expense_category,
            transaction_type="EXPENSE", description="Aluguel", amount=Decimal("1500.00"), transaction_date=start)
        response = self.client.get("/api/finance/insights/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["summary"]["income"], "5000.00")
        self.assertEqual(response.data["summary"]["expenses"], "1500.00")
        self.assertEqual(response.data["summary"]["net"], "3500.00")
        self.assertEqual(response.data["top_expense_categories"][0]["category"], "Moradia")

    def test_budget_notification_is_idempotent(self):
        today = date.today()
        month = today.replace(day=1)
        Budget.objects.create(user=self.user, category=self.expense_category, month=month, amount=Decimal("100.00"))
        Transaction.objects.create(user=self.user, account=self.account, category=self.expense_category,
            transaction_type="EXPENSE", description="Compra", amount=Decimal("85.00"), transaction_date=month)
        first = self.client.post("/api/finance/notifications/generate/")
        second = self.client.post("/api/finance/notifications/generate/")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.data["created"], 1)
        self.assertEqual(second.data["created"], 0)
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 1)

    def test_notification_is_private_and_can_be_marked_read(self):
        notification = Notification.objects.create(user=self.other, notification_type="TEST",
            severity="INFO", title="Private", message="Other user", dedupe_key="other:test")
        response = self.client.patch(f"/api/finance/notifications/{notification.id}/read/", {"is_read": True}, format="json")
        self.assertEqual(response.status_code, 404)
        own = Notification.objects.create(user=self.user, notification_type="TEST",
            severity="INFO", title="Mine", message="My notification", dedupe_key="mine:test")
        response = self.client.patch(f"/api/finance/notifications/{own.id}/read/", {"is_read": True}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["is_read"])

    def test_invalid_month_returns_400(self):
        response = self.client.get("/api/finance/insights/?month=not-a-date")
        self.assertEqual(response.status_code, 400)
