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
        income = transactions.filter(transaction_type=Transaction.TransactionType.INCOME).aggregate(total=Sum("amount"))["total"] or 0
        expenses = transactions.filter(transaction_type=Transaction.TransactionType.EXPENSE).aggregate(total=Sum("amount"))["total"] or 0
        transfers = transactions.filter(transaction_type=Transaction.TransactionType.TRANSFER).aggregate(total=Sum("amount"))["total"] or 0
        opening = Account.objects.filter(user=user, is_active=True).aggregate(total=Sum("opening_balance"))["total"] or 0
        return Response({
            "balance": opening + income - expenses,
            "income": income,
            "expenses": expenses,
            "transfers": transfers,
            "accounts_count": Account.objects.filter(user=user, is_active=True).count(),
            "categories_count": Category.objects.filter(user=user, is_active=True).count(),
            "transactions_count": transactions.count(),
        })
