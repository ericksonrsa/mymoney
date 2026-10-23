from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Account, Budget, Category, FinancialGoal, RecurringTransaction, Transaction


class Sprint11PlanningApiTests(APITestCase):
    """Regression coverage for ownership and planning APIs used by Sprint 10."""

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="planning-owner", password="StrongPass123!")
        self.other = User.objects.create_user(username="planning-other", password="StrongPass123!")
        self.client.force_authenticate(self.user)
        self.account = Account.objects.create(user=self.user, name="Conta principal")
        self.other_account = Account.objects.create(user=self.other, name="Conta privada")
        self.expense = Category.objects.create(
            user=self.user, name="Moradia", category_type=Category.CategoryType.EXPENSE
        )
        self.income = Category.objects.create(
            user=self.user, name="Salário", category_type=Category.CategoryType.INCOME
        )
        self.other_expense = Category.objects.create(
            user=self.other, name="Outra categoria", category_type=Category.CategoryType.EXPENSE
        )

    def test_budget_calculates_spend_and_rejects_income_category(self):
        month = date.today().replace(day=1)
        Budget.objects.create(user=self.user, category=self.expense, month=month, amount=Decimal("500.00"))
        Transaction.objects.create(
            user=self.user, account=self.account, category=self.expense,
            transaction_type=Transaction.TransactionType.EXPENSE,
            description="Conta de luz", amount=Decimal("125.00"), transaction_date=month,
        )

        response = self.client.get(reverse("budget-list-create"), {"month": month.isoformat()})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Decimal(str(response.data[0]["spent"])), Decimal("125.00"))
        self.assertEqual(Decimal(str(response.data[0]["remaining"])), Decimal("375.00"))
        self.assertEqual(float(response.data[0]["percentage"]), 25.0)

        invalid = self.client.post(reverse("budget-list-create"), {
            "category": str(self.income.id), "month": month.isoformat(), "amount": "100.00",
        }, format="json")
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)

    def test_budget_and_goal_lists_are_isolated_by_user(self):
        month = date.today().replace(day=1)
        Budget.objects.create(user=self.other, category=self.other_expense, month=month, amount=Decimal("200.00"))
        FinancialGoal.objects.create(
            user=self.other, name="Goal private", target_amount=Decimal("1000.00"),
            current_amount=Decimal("100.00"),
        )

        budgets = self.client.get(reverse("budget-list-create"))
        goals = self.client.get(reverse("goal-list-create"))

        self.assertEqual(budgets.status_code, status.HTTP_200_OK)
        self.assertEqual(goals.status_code, status.HTTP_200_OK)
        self.assertEqual(budgets.data, [])
        self.assertEqual(goals.data, [])

    def test_goal_progress_is_capped_and_remaining_never_negative(self):
        response = self.client.post(reverse("goal-list-create"), {
            "name": "Reserva", "target_amount": "1000.00", "current_amount": "1200.00",
            "notes": "Meta de teste",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data["percentage"]), 100.0)
        self.assertEqual(Decimal(str(response.data["remaining"])), Decimal("0"))

    def test_recurring_transaction_rejects_another_users_account(self):
        response = self.client.post(reverse("recurring-list-create"), {
            "account": str(self.other_account.id),
            "category": str(self.other_expense.id),
            "transaction_type": "EXPENSE",
            "description": "Private recurring expense",
            "amount": "50.00",
            "frequency": RecurringTransaction.Frequency.MONTHLY,
            "next_run": date.today().isoformat(),
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(RecurringTransaction.objects.filter(user=self.user).count(), 0)

    def test_planning_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)
        for route_name in ("budget-list-create", "goal-list-create", "recurring-list-create"):
            with self.subTest(route=route_name):
                response = self.client.get(reverse(route_name))
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
