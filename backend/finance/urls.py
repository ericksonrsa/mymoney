from django.urls import path
from .views import (AccountDetailView, AccountListCreateView, BudgetDetailView, BudgetListCreateView, CategoryDetailView, CategoryListCreateView, DashboardView, GoalDetailView, GoalListCreateView, TransactionDetailView, TransactionListCreateView)
urlpatterns = [
    path("accounts/", AccountListCreateView.as_view(), name="account-list-create"), path("accounts/<uuid:pk>/", AccountDetailView.as_view(), name="account-detail"),
    path("categories/", CategoryListCreateView.as_view(), name="category-list-create"), path("categories/<uuid:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path("transactions/", TransactionListCreateView.as_view(), name="transaction-list-create"), path("transactions/<uuid:pk>/", TransactionDetailView.as_view(), name="transaction-detail"),
    path("budgets/", BudgetListCreateView.as_view(), name="budget-list-create"), path("budgets/<uuid:pk>/", BudgetDetailView.as_view(), name="budget-detail"),
    path("goals/", GoalListCreateView.as_view(), name="goal-list-create"), path("goals/<uuid:pk>/", GoalDetailView.as_view(), name="goal-detail"),
    path("dashboard/", DashboardView.as_view(), name="finance-dashboard"),
]
