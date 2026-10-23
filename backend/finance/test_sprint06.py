from datetime import date, timedelta
from decimal import Decimal
import io
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import Account, Category, RecurringTransaction, Transaction

class Sprint06Tests(APITestCase):
    def setUp(self):
        User=get_user_model(); self.user=User.objects.create_user(username="sprint6",password="pass12345"); self.client.force_authenticate(self.user)
        self.account=Account.objects.create(user=self.user,name="Conta 06"); self.expense=Category.objects.create(user=self.user,name="Casa",category_type="EXPENSE"); self.income=Category.objects.create(user=self.user,name="Salário",category_type="INCOME")
    def test_recurring_generation_creates_due_transaction_and_advances(self):
        item=RecurringTransaction.objects.create(user=self.user,account=self.account,category=self.expense,transaction_type="EXPENSE",description="Aluguel",amount=Decimal("1200"),frequency="MONTHLY",next_run=date.today().replace(day=1))
        response=self.client.post("/api/finance/recurring/generate/")
        self.assertEqual(response.status_code,200); self.assertEqual(response.data["created"],1); item.refresh_from_db(); self.assertGreater(item.next_run,date.today())
        self.assertTrue(Transaction.objects.filter(description="Aluguel").exists())
    def test_recurring_isolation(self):
        User=get_user_model(); other=User.objects.create_user(username="other6",password="pass12345"); other_account=Account.objects.create(user=other,name="Other"); RecurringTransaction.objects.create(user=other,account=other_account,category=Category.objects.create(user=other,name="Other",category_type="EXPENSE"),transaction_type="EXPENSE",description="Privado",amount=10,frequency="MONTHLY",next_run=date.today())
        response=self.client.get("/api/finance/recurring/"); self.assertEqual(response.status_code,200); self.assertEqual(response.data["count"] if isinstance(response.data,dict) and "count" in response.data else len(response.data),0)
    def test_csv_upload_preview_detects_duplicate(self):
        Transaction.objects.create(user=self.user,account=self.account,category=self.expense,transaction_type="EXPENSE",description="Supermercado",amount=Decimal("55.90"),transaction_date=date(2026,10,20))
        csv_data="date;description;amount;type\n20/10/2026;Supermercado;55,90;EXPENSE\n21/10/2026;Farmácia;20,00;EXPENSE\n".encode()
        response=self.client.post("/api/finance/imports/upload/",{"account":str(self.account.id),"file":io.BytesIO(csv_data)},format="multipart")
        self.assertEqual(response.status_code,201); self.assertEqual(response.data["total_rows"],2); statuses={row["status"] for row in response.data["rows"]}; self.assertIn("DUPLICATE",statuses); self.assertIn("PENDING",statuses)
    def test_import_confirm_creates_only_pending_rows(self):
        csv_data="date;description;amount;type\n21/10/2026;Farmácia;20,00;EXPENSE\n".encode()
        response=self.client.post("/api/finance/imports/upload/",{"account":str(self.account.id),"file":io.BytesIO(csv_data)},format="multipart"); self.assertEqual(response.status_code,201); batch_id=response.data["id"]
        response=self.client.post(f"/api/finance/imports/{batch_id}/confirm/"); self.assertEqual(response.status_code,200); self.assertEqual(response.data["imported_rows"],1); self.assertTrue(Transaction.objects.filter(description="Farmácia",amount=20).exists())
