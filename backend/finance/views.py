import csv
import hashlib
import io
from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from django.db import transaction as db_transaction
from django.db.models import Q, Sum
from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Account, Budget, Category, FinancialGoal, ImportBatch, ImportRow, RecurringTransaction, Transaction
from .serializers import AccountSerializer, BudgetSerializer, CategorySerializer, FinancialGoalSerializer, ImportBatchSerializer, RecurringTransactionSerializer, TransactionSerializer

class UserOwnedMixin:
    permission_classes=(permissions.IsAuthenticated,)
    def get_queryset(self): return super().get_queryset().filter(user=self.request.user)
class AccountListCreateView(UserOwnedMixin,generics.ListCreateAPIView):
    queryset=Account.objects.all(); serializer_class=AccountSerializer
    def perform_create(self,s): s.save(user=self.request.user)
class AccountDetailView(UserOwnedMixin,generics.RetrieveUpdateDestroyAPIView): queryset=Account.objects.all(); serializer_class=AccountSerializer
class CategoryListCreateView(UserOwnedMixin,generics.ListCreateAPIView):
    queryset=Category.objects.all(); serializer_class=CategorySerializer
    def get_queryset(self):
        q=super().get_queryset(); t=self.request.query_params.get("type"); return q.filter(category_type=t.upper()) if t else q
    def perform_create(self,s): s.save(user=self.request.user)
class CategoryDetailView(UserOwnedMixin,generics.RetrieveUpdateDestroyAPIView): queryset=Category.objects.all(); serializer_class=CategorySerializer
class TransactionListCreateView(UserOwnedMixin,generics.ListCreateAPIView):
    queryset=Transaction.objects.select_related("account","destination_account","category").all(); serializer_class=TransactionSerializer
    def get_queryset(self):
        q=super().get_queryset(); p=self.request.query_params
        if p.get("type"): q=q.filter(transaction_type=p["type"].upper())
        if p.get("account"): q=q.filter(Q(account_id=p["account"])|Q(destination_account_id=p["account"]))
        if p.get("category"): q=q.filter(category_id=p["category"])
        if p.get("date_from"): q=q.filter(transaction_date__gte=p["date_from"])
        if p.get("date_to"): q=q.filter(transaction_date__lte=p["date_to"])
        if p.get("q"): q=q.filter(Q(description__icontains=p["q"].strip())|Q(notes__icontains=p["q"].strip()))
        if p.get("amount_min"): q=q.filter(amount__gte=p["amount_min"])
        if p.get("amount_max"): q=q.filter(amount__lte=p["amount_max"])
        allowed={"transaction_date","-transaction_date","amount","-amount","created_at","-created_at"}; ordering=[x for x in p.get("ordering","-transaction_date,-created_at").split(",") if x in allowed]
        return q.order_by(*(ordering or ["-transaction_date","-created_at"]));
    def perform_create(self,s): s.save(user=self.request.user)
class TransactionDetailView(UserOwnedMixin,generics.RetrieveUpdateDestroyAPIView): queryset=Transaction.objects.select_related("account","destination_account","category").all(); serializer_class=TransactionSerializer
class BudgetListCreateView(UserOwnedMixin,generics.ListCreateAPIView):
    queryset=Budget.objects.select_related("category").all(); serializer_class=BudgetSerializer
    def get_queryset(self):
        q=super().get_queryset(); m=self.request.query_params.get("month"); return q.filter(month=m) if m else q
    def perform_create(self,s): s.save(user=self.request.user)
class BudgetDetailView(UserOwnedMixin,generics.RetrieveUpdateDestroyAPIView): queryset=Budget.objects.select_related("category").all(); serializer_class=BudgetSerializer
class GoalListCreateView(UserOwnedMixin,generics.ListCreateAPIView):
    queryset=FinancialGoal.objects.all(); serializer_class=FinancialGoalSerializer
    def perform_create(self,s): s.save(user=self.request.user)
class GoalDetailView(UserOwnedMixin,generics.RetrieveUpdateDestroyAPIView): queryset=FinancialGoal.objects.all(); serializer_class=FinancialGoalSerializer
class RecurringListCreateView(UserOwnedMixin,generics.ListCreateAPIView):
    queryset=RecurringTransaction.objects.select_related("account","category").all(); serializer_class=RecurringTransactionSerializer
    def get_queryset(self):
        q=super().get_queryset(); active=self.request.query_params.get("active")
        return q.filter(is_active=active.lower()=="true") if active else q
    def perform_create(self,s): s.save(user=self.request.user)
class RecurringDetailView(UserOwnedMixin,generics.RetrieveUpdateDestroyAPIView): queryset=RecurringTransaction.objects.select_related("account","category").all(); serializer_class=RecurringTransactionSerializer

def advance_schedule(d,frequency):
    if frequency==RecurringTransaction.Frequency.WEEKLY: return d+timedelta(days=7)
    if frequency==RecurringTransaction.Frequency.YEARLY: return d.replace(year=d.year+1)
    day=d.day; year=d.year+(d.month//12); month=d.month%12+1; return d.replace(year=year,month=month,day=min(day,monthrange(year,month)[1]))

class GenerateRecurringView(APIView):
    permission_classes=(permissions.IsAuthenticated,)
    def post(self,request):
        today=date.today(); created=[]
        recurring=RecurringTransaction.objects.filter(user=request.user,is_active=True,next_run__lte=today).select_related("account","category")
        with db_transaction.atomic():
            for item in recurring:
                while item.next_run<=today and (not item.end_date or item.next_run<=item.end_date):
                    exists=Transaction.objects.filter(user=request.user,account=item.account,transaction_date=item.next_run,description=item.description,amount=item.amount,transaction_type=item.transaction_type).exists()
                    if not exists:
                        created.append(Transaction.objects.create(user=request.user,account=item.account,category=item.category,transaction_type=item.transaction_type,description=item.description,amount=item.amount,transaction_date=item.next_run,notes=item.notes))
                    item.next_run=advance_schedule(item.next_run,item.frequency)
                if item.end_date and item.next_run>item.end_date: item.is_active=False
                item.save(update_fields=["next_run","is_active","updated_at"])
        return Response({"created":len(created),"transactions":[str(x.id) for x in created]})

class DashboardView(APIView):
    permission_classes=(permissions.IsAuthenticated,)
    def get(self,request):
        user=request.user; transactions=Transaction.objects.filter(user=user); today=date.today()
        try: start=date.fromisoformat(request.query_params.get("date_from")) if request.query_params.get("date_from") else today.replace(day=1)
        except ValueError: start=today.replace(day=1)
        try: end=date.fromisoformat(request.query_params.get("date_to")) if request.query_params.get("date_to") else today
        except ValueError: end=today
        if start>end: start,end=end,start
        pt=transactions.filter(transaction_date__range=(start,end)); income=pt.filter(transaction_type="INCOME").aggregate(total=Sum("amount"))["total"] or 0; expenses=pt.filter(transaction_type="EXPENSE").aggregate(total=Sum("amount"))["total"] or 0; transfers=pt.filter(transaction_type="TRANSFER").aggregate(total=Sum("amount"))["total"] or 0; opening=Account.objects.filter(user=user,is_active=True).aggregate(total=Sum("opening_balance"))["total"] or 0
        rows=pt.filter(transaction_type="EXPENSE").values("category__name").annotate(total=Sum("amount")).order_by("-total")[:8]; category_expenses=[{"category":r["category__name"] or "Sem categoria","amount":float(r["total"])} for r in rows]
        monthly=pt.values("transaction_date__year","transaction_date__month").annotate(income=Sum("amount",filter=Q(transaction_type="INCOME")),expenses=Sum("amount",filter=Q(transaction_type="EXPENSE"))).order_by("transaction_date__year","transaction_date__month"); cash_flow=[{"month":f"{r['transaction_date__year']}-{r['transaction_date__month']:02d}","income":float(r["income"] or 0),"expenses":float(r["expenses"] or 0),"net":float((r["income"] or 0)-(r["expenses"] or 0))} for r in monthly]
        months=[]; cursor=start.replace(day=1)
        while cursor<=end.replace(day=1): months.append(cursor); cursor=(cursor.replace(day=28)+timedelta(days=4)).replace(day=1)
        mm={x["month"]:x for x in cash_flow}; running=float(opening); net_worth=[]
        for month in months:
            key=f"{month.year}-{month.month:02d}"; item=mm.get(key,{"income":0,"expenses":0}); running+=item["income"]-item["expenses"]; net_worth.append({"month":key,"value":round(running,2)})
        return Response({"balance":float(opening+income-expenses),"income":float(income),"expenses":float(expenses),"transfers":float(transfers),"accounts_count":Account.objects.filter(user=user,is_active=True).count(),"categories_count":Category.objects.filter(user=user,is_active=True).count(),"transactions_count":pt.count(),"period":{"date_from":start.isoformat(),"date_to":end.isoformat()},"category_expenses":category_expenses,"cash_flow":cash_flow,"net_worth":net_worth})

def parse_amount(raw):
    value=str(raw).strip().replace("R$","").replace(" ","")
    if "," in value and "." in value: value=value.replace(".","").replace(",",".")
    elif "," in value: value=value.replace(",",".")
    return Decimal(value)

def parse_import_csv(data):
    text=data.decode("utf-8-sig")
    sample=text[:4096]; dialect=csv.Sniffer().sniff(sample,delimiters=",;\t")
    reader=csv.DictReader(io.StringIO(text),dialect=dialect)
    aliases={"date":{"date","data","transaction_date","data_transacao"},"description":{"description","descricao","descrição","memo","historico","histórico"},"amount":{"amount","valor","value"},"type":{"type","tipo","transaction_type","natureza"}}
    def pick(row,names):
        for key in row:
            if key and key.strip().lower() in names:return row[key]
        return None
    rows=[]
    for raw in reader:
        d=pick(raw,aliases["date"]); desc=pick(raw,aliases["description"]); amount=pick(raw,aliases["amount"]); kind=pick(raw,aliases["type"])
        if not d and not desc and not amount: continue
        try:
            dt=date.fromisoformat(d.strip()) if d and len(d.strip())==10 and d[4:5]=="-" else date.fromisoformat("-".join(reversed(d.strip().split("/"))))
            value=parse_amount(amount)
            if value<0: value=-value; inferred="EXPENSE"
            else: inferred="INCOME"
            k=(kind or inferred).strip().upper()
            if k in {"D","DEBIT","DESPESA","EXPENSE","SAIDA","SAÍDA"}: k="EXPENSE"
            elif k in {"C","CREDIT","RECEITA","INCOME","ENTRADA"}: k="INCOME"
            else: k=inferred
            if k not in {"INCOME","EXPENSE"}: raise ValueError("tipo inválido")
            desc=(desc or "Importação bancária").strip()[:200]
            fingerprint=hashlib.sha256(f"{dt.isoformat()}|{desc.lower()}|{value:.2f}|{k}".encode()).hexdigest()
            rows.append((dt,desc,value,k,fingerprint,""))
        except (ValueError,InvalidOperation,AttributeError) as exc: rows.append((date.today(),str(desc or "")[:200],Decimal("0.00"),"EXPENSE",hashlib.sha256(str(raw).encode()).hexdigest(),f"Linha inválida: {exc}"))
    return rows

class ImportBatchListView(UserOwnedMixin,generics.ListAPIView):
    queryset=ImportBatch.objects.all(); serializer_class=ImportBatchSerializer
class ImportUploadView(APIView):
    permission_classes=(permissions.IsAuthenticated,); parser_classes=(MultiPartParser,FormParser)
    def post(self,request):
        upload=request.FILES.get("file"); account_id=request.data.get("account")
        if not upload:return Response({"file":"Arquivo CSV é obrigatório."},status=400)
        account=Account.objects.filter(id=account_id,user=request.user).first()
        if not account:return Response({"account":"Conta inválida."},status=400)
        if not upload.name.lower().endswith(".csv"):return Response({"file":"Sprint 06 aceita arquivos CSV UTF-8."},status=400)
        try: rows=parse_import_csv(upload.read())
        except (UnicodeDecodeError,csv.Error) as exc:return Response({"file":f"CSV inválido: {exc}"},status=400)
        batch=ImportBatch.objects.create(user=request.user,account=account,filename=upload.name,total_rows=len(rows))
        for dt,desc,amount,kind,fingerprint,error in rows:
            duplicate=Transaction.objects.filter(user=request.user,account=account,transaction_date=dt,description=desc,amount=amount,transaction_type=kind).exists()
            ImportRow.objects.create(batch=batch,transaction_date=dt,description=desc,amount=amount,transaction_type=kind,fingerprint=fingerprint,status="DUPLICATE" if duplicate else ("ERROR" if error else "PENDING"),error=error)
        return Response(ImportBatchSerializer(batch,context={"request":request}).data,status=201)
class ImportConfirmView(APIView):
    permission_classes=(permissions.IsAuthenticated,)
    def post(self,request,pk):
        batch=ImportBatch.objects.filter(id=pk,user=request.user,status=ImportBatch.Status.PREVIEW).first()
        if not batch:return Response({"detail":"Lote não encontrado ou já processado."},status=404)
        imported=0
        with db_transaction.atomic():
            for row in batch.rows.filter(status="PENDING"):
                if Transaction.objects.filter(user=request.user,account=batch.account,transaction_date=row.transaction_date,description=row.description,amount=row.amount,transaction_type=row.transaction_type).exists(): row.status="DUPLICATE"; row.save(update_fields=["status"]); continue
                cat=Category.objects.filter(user=request.user,category_type=row.transaction_type,is_active=True).order_by("name").first()
                if not cat: row.status="ERROR"; row.error="Crie uma categoria compatível antes de confirmar a importação."; row.save(update_fields=["status","error"]); continue
                tx=Transaction.objects.create(user=request.user,account=batch.account,category=cat,transaction_type=row.transaction_type,description=row.description,amount=row.amount,transaction_date=row.transaction_date,notes="Importado via CSV")
                row.transaction=tx; row.status="IMPORTED"; row.save(update_fields=["transaction","status"]); imported+=1
            batch.imported_rows=imported; batch.status=ImportBatch.Status.IMPORTED; batch.save(update_fields=["imported_rows","status"])
        return Response(ImportBatchSerializer(batch,context={"request":request}).data)
