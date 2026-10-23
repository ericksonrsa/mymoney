from calendar import monthrange
from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Budget, Category, FinancialGoal, Notification, RecurringTransaction, Transaction


def month_window(value):
    start = value.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


class NotificationListView(generics.ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user)
        unread = self.request.query_params.get("unread")
        if unread is not None:
            qs = qs.filter(is_read=unread.lower() == "true")
        return qs.order_by("is_read", "-created_at")

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(qs)
        items = page if page is not None else qs
        data = [{
            "id": str(n.id), "notification_type": n.notification_type,
            "severity": n.severity, "title": n.title, "message": n.message,
            "is_read": n.is_read, "created_at": n.created_at.isoformat(),
            "metadata": n.metadata,
        } for n in items]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        if page is not None:
            response = self.get_paginated_response(data)
            response.data["unread_count"] = unread_count
            return response
        return Response({"unread_count": unread_count, "results": data})


class NotificationReadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk):
        notification = Notification.objects.filter(pk=pk, user=request.user).first()
        if notification is None:
            return Response({"detail": "Notificação não encontrada."}, status=status.HTTP_404_NOT_FOUND)
        notification.is_read = bool(request.data.get("is_read", True))
        notification.save(update_fields=["is_read"])
        return Response({"id": str(notification.id), "is_read": notification.is_read})


class GenerateNotificationsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        today = timezone.localdate()
        created = 0

        def add(key, kind, severity, title, message, metadata=None):
            nonlocal created
            _, was_created = Notification.objects.get_or_create(
                user=request.user, dedupe_key=key,
                defaults={"notification_type": kind, "severity": severity,
                          "title": title, "message": message, "metadata": metadata or {}},
            )
            created += int(was_created)

        # Notify when a monthly expense budget reaches 80% or is exceeded.
        current_month = today.replace(day=1)
        budgets = Budget.objects.filter(user=request.user, month=current_month).select_related("category")
        for budget in budgets:
            end = month_window(current_month)[1]
            spent = Transaction.objects.filter(
                user=request.user, category=budget.category, transaction_type="EXPENSE",
                transaction_date__gte=current_month, transaction_date__lt=end,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
            percentage = (spent / budget.amount * 100) if budget.amount else Decimal("0")
            if percentage >= 80:
                severity = "CRITICAL" if percentage >= 100 else "WARNING"
                add(
                    f"budget:{budget.id}:{current_month.isoformat()}", "BUDGET_THRESHOLD", severity,
                    "Orçamento no limite" if percentage < 100 else "Orçamento ultrapassado",
                    f"{budget.category.name}: {percentage:.0f}% do orçamento utilizado.",
                    {"budget_id": str(budget.id), "category": budget.category.name,
                     "spent": str(spent), "budget": str(budget.amount), "percentage": round(float(percentage), 2)},
                )

        # Upcoming recurring entries are reminders only; they are not generated here.
        for item in RecurringTransaction.objects.filter(
            user=request.user, is_active=True, next_run__gte=today, next_run__lte=today + timedelta(days=7)
        ).select_related("account"):
            add(
                f"recurring:{item.id}:{item.next_run.isoformat()}", "UPCOMING_TRANSACTION", "INFO",
                "Lançamento recorrente próximo",
                f"{item.description} de {item.amount} previsto para {item.next_run.isoformat()}.",
                {"recurring_id": str(item.id), "account": item.account.name,
                 "amount": str(item.amount), "due_date": item.next_run.isoformat()},
            )

        # Goal reminders are generated once per goal when its target date is within 30 days.
        for goal in FinancialGoal.objects.filter(
            user=request.user, is_active=True, target_date__gte=today,
            target_date__lte=today + timedelta(days=30),
        ):
            add(
                f"goal:{goal.id}:{goal.target_date.isoformat()}", "GOAL_DEADLINE", "INFO",
                "Meta financeira se aproximando",
                f"A meta '{goal.name}' tem prazo em {goal.target_date.isoformat()}.",
                {"goal_id": str(goal.id), "target_date": goal.target_date.isoformat(),
                 "percentage": round(min(float(goal.current_amount / goal.target_amount * 100), 100), 2)},
            )

        return Response({"created": created, "unread_count": Notification.objects.filter(user=request.user, is_read=False).count()})


class FinancialInsightsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        today = timezone.localdate()
        raw_month = request.query_params.get("month")
        try:
            month = date.fromisoformat(raw_month) if raw_month else today.replace(day=1)
            month = month.replace(day=1)
        except ValueError:
            return Response({"month": ["Informe uma data válida no formato YYYY-MM-DD."]}, status=400)

        start, end = month_window(month)
        previous_end = start
        previous_start = (start - timedelta(days=1)).replace(day=1)

        def totals(begin, finish):
            rows = Transaction.objects.filter(
                user=request.user, transaction_date__gte=begin, transaction_date__lt=finish,
            )
            income = rows.filter(transaction_type="INCOME").aggregate(total=Sum("amount"))["total"] or Decimal("0")
            expense = rows.filter(transaction_type="EXPENSE").aggregate(total=Sum("amount"))["total"] or Decimal("0")
            return income, expense

        income, expense = totals(start, end)
        previous_income, previous_expense = totals(previous_start, previous_end)
        category_rows = Transaction.objects.filter(
            user=request.user, transaction_type="EXPENSE",
            transaction_date__gte=start, transaction_date__lt=end,
        ).values("category_id", "category__name").annotate(total=Sum("amount")).order_by("-total")[:5]

        budgets = []
        for budget in Budget.objects.filter(user=request.user, month=start).select_related("category"):
            spent = Transaction.objects.filter(
                user=request.user, category=budget.category, transaction_type="EXPENSE",
                transaction_date__gte=start, transaction_date__lt=end,
            ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
            budgets.append({
                "id": str(budget.id), "category": budget.category.name, "amount": str(budget.amount),
                "spent": str(spent), "remaining": str(budget.amount - spent),
                "percentage": round(float(spent / budget.amount * 100), 2) if budget.amount else 0,
            })

        active_goals = FinancialGoal.objects.filter(user=request.user, is_active=True)
        goal_summary = [{
            "id": str(g.id), "name": g.name, "target_amount": str(g.target_amount),
            "current_amount": str(g.current_amount),
            "percentage": round(min(float(g.current_amount / g.target_amount * 100), 100), 2),
            "target_date": g.target_date.isoformat() if g.target_date else None,
        } for g in active_goals]

        def change(current, previous):
            if previous == 0:
                return None if current == 0 else 100.0
            return round(float((current - previous) / previous * 100), 2)

        return Response({
            "month": start.isoformat(),
            "summary": {
                "income": str(income), "expenses": str(expense), "net": str(income - expense),
                "previous_income": str(previous_income), "previous_expenses": str(previous_expense),
                "income_change_percent": change(income, previous_income),
                "expense_change_percent": change(expense, previous_expense),
            },
            "top_expense_categories": [{
                "category_id": str(row["category_id"]) if row["category_id"] else None,
                "category": row["category__name"] or "Sem categoria", "amount": str(row["total"]),
            } for row in category_rows],
            "budgets": budgets,
            "goals": goal_summary,
            "upcoming_recurring": [{
                "id": str(item.id), "description": item.description, "amount": str(item.amount),
                "next_run": item.next_run.isoformat(), "account": item.account.name,
            } for item in RecurringTransaction.objects.filter(
                user=request.user, is_active=True, next_run__gte=today,
                next_run__lte=today + timedelta(days=30),
            ).select_related("account").order_by("next_run")],
        })
