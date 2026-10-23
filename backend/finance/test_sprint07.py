from datetime import date
from decimal import Decimal
import io
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Account, CategorizationRule, Category, ImportBatch, ImportRow, Transaction


class Sprint07Tests(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="sprint7", password="pass12345")
        self.client.force_authenticate(self.user)
        self.account = Account.objects.create(user=self.user, name="Conta 07")
        self.food = Category.objects.create(user=self.user, name="Alimentação", category_type="EXPENSE")
        self.home = Category.objects.create(user=self.user, name="Moradia", category_type="EXPENSE")

    def test_rule_creation_validates_category_ownership(self):
        User = get_user_model()
        other = User.objects.create_user(username="other7", password="pass12345")
        category = Category.objects.create(user=other, name="Privada", category_type="EXPENSE")
        response = self.client.post("/api/finance/categorization/rules/", {
            "name": "Mercado", "pattern": "mercado", "match_field": "DESCRIPTION",
            "category": str(category.id), "priority": 1,
        }, format="json")
        self.assertEqual(response.status_code, 400)

    def test_smart_import_uses_highest_priority_matching_rule(self):
        batch = ImportBatch.objects.create(user=self.user, account=self.account, filename="bank.csv", total_rows=1)
        row = ImportRow.objects.create(batch=batch, transaction_date=date(2026, 10, 21), description="Mercado Central", amount=Decimal("42.50"), transaction_type="EXPENSE", fingerprint="a"*64)
        CategorizationRule.objects.create(user=self.user, name="Mercado", pattern="mercado", category=self.food, priority=10)
        CategorizationRule.objects.create(user=self.user, name="Central", pattern="central", category=self.home, priority=20)
        response = self.client.post(f"/api/finance/imports/{batch.id}/confirm-smart/")
        self.assertEqual(response.status_code, 200)
        row.refresh_from_db()
        self.assertEqual(row.status, "IMPORTED")
        self.assertEqual(row.transaction.category, self.food)

    def test_reconciliation_returns_exact_and_possible_matches(self):
        batch = ImportBatch.objects.create(user=self.user, account=self.account, filename="bank.csv", total_rows=2)
        exact = Transaction.objects.create(user=self.user, account=self.account, category=self.food, transaction_type="EXPENSE", description="Café", amount=Decimal("12.00"), transaction_date=date(2026, 10, 20))
        ImportRow.objects.create(batch=batch, transaction_date=date(2026, 10, 20), description="Café", amount=Decimal("12.00"), transaction_type="EXPENSE", fingerprint="b"*64)
        Transaction.objects.create(user=self.user, account=self.account, category=self.food, transaction_type="EXPENSE", description="Farmácia", amount=Decimal("18.00"), transaction_date=date(2026, 10, 21))
        ImportRow.objects.create(batch=batch, transaction_date=date(2026, 10, 22), description="Drogaria", amount=Decimal("18.00"), transaction_type="EXPENSE", fingerprint="c"*64)
        response = self.client.get(f"/api/finance/imports/{batch.id}/reconcile/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["rows"][0]["status"], "EXACT_MATCH")
        self.assertEqual(response.data["rows"][1]["status"], "POSSIBLE_MATCH")

    def test_rule_list_is_user_isolated(self):
        User = get_user_model()
        other = User.objects.create_user(username="other_rules", password="pass12345")
        other_account = Account.objects.create(user=other, name="Other")
        other_category = Category.objects.create(user=other, name="Other expense", category_type="EXPENSE")
        CategorizationRule.objects.create(user=other, name="Private", pattern="private", category=other_category)
        response = self.client.get("/api/finance/categorization/rules/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
