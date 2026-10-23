from rest_framework import generics, permissions
from .models import Invoice
from .serializers import InvoiceSerializer


class InvoiceListCreateView(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.prefetch_related("transactions__account", "transactions__category").all()

    def get_queryset(self):
        queryset = super().get_queryset().filter(user=self.request.user)
        status_filter = self.request.query_params.get("status")
        if status_filter in {choice.value for choice in Invoice.Status}:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.prefetch_related("transactions__account", "transactions__category").all()

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
