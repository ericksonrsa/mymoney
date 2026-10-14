from django.urls import path

from .views import (
    AccountDetailView,
    AccountListCreateView,
    CategoryDetailView,
    CategoryListCreateView,
    DashboardView,
    TransactionDetailView,
    TransactionListCreateView,
)

urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"),
    path("accounts/<uuid:pk>/", AccountDetailView.as_view(), name="account-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"),
    path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list-create"),
    path("transactions/<uuid:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("dashboard/", DashboardView.as_view(), name="finance-dashboard"),
]
