from datetime import date, timedelta

from django.db.models import Q, Sum
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Account, Category, Transaction
from .serializers import AccountSerializer, CategorySerializer, TransactionSerializer


class UserOwnedMixin:
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class AccountListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


class CategoryListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category_type = self.request.query_params.get("type")
        if category_type:
            queryset = queryset.filter(category_type=category_type.upper())
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TransactionListCreateView(UserOwnedMixin, generics.ListCreateAPIView):
    queryset = Transaction.objects.select_related("account", "destination_account", "category").all()
    serializer_class = TransactionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        if params.get("type"):
            queryset = queryset.filter(transaction_type=params["type"].upper())
        if params.get("account"):
            queryset = queryset.filter(Q(account_id=params["account"]) | Q(destination_account_id=params["account"]))
        if params.get("category"):
            queryset = queryset.filter(category_id=params["category"])
        if params.get("date_from"):
            queryset = queryset.filter(transaction_date__gte=params["date_from"])
        if params.get("date_to"):
            queryset = queryset.filter(transaction_date__lte=params["date_to"])
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionDetailView(UserOwnedMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = Transaction.objects.select_related("account", "destination_account", "category").all()
    serializer_class = TransactionSerializer


class DashboardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = request.user
        transactions = Transaction.objects.filter(user=user)
        today = date.today()
        date_from = request.query_params.get("date_from")
        date_to = request.query_params.get("date_to")
        try:
            start = date.fromisoformat(date_from) if date_from else today.replace(day=1)
        except ValueError:
            start = today.replace(day=1)
        try:
            end = date.fromisoformat(date_to) if date_to else today
        except ValueError:
            end = today
        if start > end:
            start, end = end, start

        period_transactions = transactions.filter(transaction_date__range=(start, end))
        income = period_transactions.filter(transaction_type=Transaction.TransactionType.INCOME).aggregate(total=Sum("amount"))["total"] or 0
        expenses = period_transactions.filter(transaction_type=Transaction.TransactionType.EXPENSE).aggregate(total=Sum("amount"))["total"] or 0
        transfers = period_transactions.filter(transaction_type=Transaction.TransactionType.TRANSFER).aggregate(total=Sum("amount"))["total"] or 0
        opening = Account.objects.filter(user=user, is_active=True).aggregate(total=Sum("opening_balance"))["total"] or 0

        category_rows = period_transactions.filter(transaction_type=Transaction.TransactionType.EXPENSE).values("category__name").annotate(total=Sum("amount")).order_by("-total")[:8]
        category_expenses = [{"category": row["category__name"] or "Sem categoria", "amount": float(row["total"])} for row in category_rows]

        monthly_rows = period_transactions.values("transaction_date__year", "transaction_date__month").annotate(
            income=Sum("amount", filter=Q(transaction_type=Transaction.TransactionType.INCOME)),
            expenses=Sum("amount", filter=Q(transaction_type=Transaction.TransactionType.EXPENSE)),
        ).order_by("transaction_date__year", "transaction_date__month")
        cash_flow = [{
            "month": f"{row['transaction_date__year']}-{row['transaction_date__month']:02d}",
            "income": float(row["income"] or 0),
            "expenses": float(row["expenses"] or 0),
            "net": float((row["income"] or 0) - (row["expenses"] or 0)),
        } for row in monthly_rows]

        months = []
        cursor = start.replace(day=1)
        while cursor <= end.replace(day=1):
            months.append(cursor)
            cursor = (cursor.replace(day=28) + timedelta(days=4)).replace(day=1)
        monthly_map = {item["month"]: item for item in cash_flow}
        running = float(opening)
        net_worth = []
        for month in months:
            key = f"{month.year}-{month.month:02d}"
            item = monthly_map.get(key, {"income": 0, "expenses": 0})
            running += item["income"] - item["expenses"]
            net_worth.append({"month": key, "value": round(running, 2)})

        return Response({
            "balance": float(opening + income - expenses),
            "income": float(income),
            "expenses": float(expenses),
            "transfers": float(transfers),
            "accounts_count": Account.objects.filter(user=user, is_active=True).count(),
            "categories_count": Category.objects.filter(user=user, is_active=True).count(),
            "transactions_count": period_transactions.count(),
            "period": {"date_from": start.isoformat(), "date_to": end.isoformat()},
            "category_expenses": category_expenses,
            "cash_flow": cash_flow,
            "net_worth": net_worth,
        })
