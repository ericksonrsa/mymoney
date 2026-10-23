from datetime import date, timedelta
from django.db.models import Q, Sum
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Account, Budget, Category, FinancialGoal, Transaction
from .serializers import AccountSerializer, BudgetSerializer, CategorySerializer, FinancialGoalSerializer, TransactionSerializer

class UserOwnedMixin:
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self): return super().get_queryset().filter(user=self.request.user)
class AccountListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset=Account.objects.all(); serializer_class=AccountSerializer
    def perform_create(self, serializer): serializer.save(user=self.request.user)
class AccountDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView): queryset=Account.objects.all(); serializer_class=AccountSerializer
class CategoryListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset=Category.objects.all(); serializer_class=CategorySerializer
    def get_queryset(self):
        q=super().get_queryset(); t=self.request.query_params.get("type"); return q.filter(category_type=t.upper()) if t else q
    def perform_create(self, serializer): serializer.save(user=self.request.user)
class CategoryDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView): queryset=Category.objects.all(); serializer_class=CategorySerializer
class TransactionListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
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
    def perform_create(self, serializer): serializer.save(user=self.request.user)
class TransactionDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView): queryset=Transaction.objects.select_related("account","destination_account","category").all(); serializer_class=TransactionSerializer
class BudgetListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset=Budget.objects.select_related("category").all(); serializer_class=BudgetSerializer
    def get_queryset(self):
        q=super().get_queryset(); m=self.request.query_params.get("month"); return q.filter(month=m) if m else q
    def perform_create(self, serializer): serializer.save(user=self.request.user)
class BudgetDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView): queryset=Budget.objects.select_related("category").all(); serializer_class=BudgetSerializer
class GoalListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset=FinancialGoal.objects.all(); serializer_class=FinancialGoalSerializer
    def perform_create(self, serializer): serializer.save(user=self.request.user)
class GoalDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView): queryset=FinancialGoal.objects.all(); serializer_class=FinancialGoalSerializer

class DashboardView(APIView):
    permission_classes=(permissions.IsAuthenticated,)
    def get(self, request):
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
