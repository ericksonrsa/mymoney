from datetime import timedelta
from django.db import transaction as db_transaction
from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CategorizationRule, Category, ImportBatch, Transaction
from .serializers import CategorizationRuleSerializer, ImportBatchSerializer


class RuleOwnerMixin:
    permission_classes = (permissions.IsAuthenticated,)
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class CategorizationRuleListCreateView(RuleOwnerMixin, generics.ListCreateAPIView):
    queryset = CategorizationRule.objects.select_related("category").all()
    serializer_class = CategorizationRuleSerializer
    def get_queryset(self):
        qs = super().get_queryset()
        active = self.request.query_params.get("active")
        return qs.filter(is_active=active.lower() == "true") if active else qs
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategorizationRuleDetailView(RuleOwnerMixin, generics.RetrieveUpdateDestroyAPIView):
    queryset = CategorizationRule.objects.select_related("category").all()
    serializer_class = CategorizationRuleSerializer


class ImportReconciliationView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        batch = ImportBatch.objects.filter(pk=pk, user=request.user).first()
        if not batch:
            return Response({"detail": "Lote não encontrado."}, status=404)
        results = []
        for row in batch.rows.all().order_by("id"):
            exact = Transaction.objects.filter(
                user=request.user, account=batch.account,
                transaction_date=row.transaction_date, amount=row.amount,
                transaction_type=row.transaction_type, description__iexact=row.description,
            ).first()
            candidates = []
            if not exact:
                candidates = list(Transaction.objects.filter(
                    user=request.user, account=batch.account, amount=row.amount,
                    transaction_type=row.transaction_type,
                    transaction_date__range=(row.transaction_date - timedelta(days=3), row.transaction_date + timedelta(days=3)),
                ).exclude(pk=row.transaction_id).order_by("transaction_date")[:5])
            results.append({
                "row_id": str(row.id),
                "status": "EXACT_MATCH" if exact else ("POSSIBLE_MATCH" if candidates else row.status),
                "exact_transaction_id": str(exact.id) if exact else None,
                "candidates": [{
                    "id": str(tx.id), "date": tx.transaction_date.isoformat(),
                    "description": tx.description, "amount": str(tx.amount),
                } for tx in candidates],
            })
        return Response({"batch_id": str(batch.id), "status": batch.status, "rows": results})


class SmartImportConfirmView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        batch = ImportBatch.objects.filter(pk=pk, user=request.user, status=ImportBatch.Status.PREVIEW).first()
        if not batch:
            return Response({"detail": "Lote não encontrado ou já processado."}, status=404)
        rules = list(CategorizationRule.objects.filter(user=request.user, is_active=True).select_related("category").order_by("priority", "name"))
        imported = 0
        with db_transaction.atomic():
            for row in batch.rows.select_for_update().filter(status="PENDING"):
                if Transaction.objects.filter(
                    user=request.user, account=batch.account, transaction_date=row.transaction_date,
                    description__iexact=row.description, amount=row.amount,
                    transaction_type=row.transaction_type,
                ).exists():
                    row.status = "DUPLICATE"
                    row.save(update_fields=["status"])
                    continue
                category = None
                for rule in rules:
                    if rule.category.category_type != row.transaction_type:
                        continue
                    source = row.description if rule.match_field == CategorizationRule.MatchField.DESCRIPTION else ""
                    if rule.pattern.casefold() in source.casefold():
                        category = rule.category
                        break
                if category is None:
                    category = Category.objects.filter(
                        user=request.user, category_type=row.transaction_type, is_active=True
                    ).order_by("name").first()
                if category is None:
                    row.status = "ERROR"
                    row.error = "Nenhuma categoria compatível ativa. Crie uma categoria ou regra antes de confirmar."
                    row.save(update_fields=["status", "error"])
                    continue
                tx = Transaction.objects.create(
                    user=request.user, account=batch.account, category=category,
                    transaction_type=row.transaction_type, description=row.description,
                    amount=row.amount, transaction_date=row.transaction_date,
                    notes="Importado via CSV (categorização inteligente)",
                )
                row.transaction = tx
                row.status = "IMPORTED"
                row.save(update_fields=["transaction", "status"])
                imported += 1
            batch.imported_rows = imported
            batch.status = ImportBatch.Status.IMPORTED
            batch.save(update_fields=["imported_rows", "status"])
        return Response(ImportBatchSerializer(batch, context={"request": request}).data)
