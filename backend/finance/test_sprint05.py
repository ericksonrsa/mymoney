from datetime import date
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Account, Budget, Category, FinancialGoal, Transaction

class Sprint05ApiTests(APITestCase):
    def setUp(self):
        User=get_user_model(); self.user=User.objects.create_user(username="budget-owner",password="StrongPass123!"); self.other=User.objects.create_user(username="budget-other",password="StrongPass123!"); self.client.force_authenticate(self.user)
        self.account=Account.objects.create(user=self.user,name="Conta Principal",opening_balance=Decimal("1000")); self.category=Category.objects.create(user=self.user,name="Alimentação",category_type="EXPENSE")
    def test_budget_reports_spending_and_percentage(self):
        budget=Budget.objects.create(user=self.user,category=self.category,month=date(2026,10,1),amount=Decimal("1000")); Transaction.objects.create(user=self.user,account=self.account,category=self.category,transaction_type="EXPENSE",description="Mercado",amount=Decimal("250"),transaction_date=date(2026,10,10))
        response=self.client.get(reverse("budget-list-create")); self.assertEqual(response.status_code,status.HTTP_200_OK); item=response.data[0]; self.assertEqual(item["spent"],250.0); self.assertEqual(item["remaining"],750.0); self.assertEqual(item["percentage"],25.0)
    def test_budget_cannot_use_income_category(self):
        income=Category.objects.create(user=self.user,name="Salário",category_type="INCOME"); response=self.client.post(reverse("budget-list-create"),{"category":str(income.id),"month":"2026-10-01","amount":"1000"},format="json"); self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
    def test_budget_isolation(self):
        Budget.objects.create(user=self.other,category=Category.objects.create(user=self.other,name="Other",category_type="EXPENSE"),month=date(2026,10,1),amount=Decimal("500")); self.assertEqual(self.client.get(reverse("budget-list-create")).data,[])
    def test_goal_progress(self):
        goal=FinancialGoal.objects.create(user=self.user,name="Reserva",target_amount=Decimal("10000"),current_amount=Decimal("2500"),target_date=date(2027,10,1)); response=self.client.get(reverse("goal-list-create")); self.assertEqual(response.data[0]["percentage"],25.0); self.assertEqual(response.data[0]["remaining"],7500.0)
    def test_goal_isolation(self):
        FinancialGoal.objects.create(user=self.other,name="Other Goal",target_amount=Decimal("1000")); self.assertEqual(self.client.get(reverse("goal-list-create")).data,[])
