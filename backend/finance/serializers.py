from rest_framework import serializers

from .models import Account, Category, Transaction


class AccountSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = ("id", "name", "institution", "account_type", "opening_balance", "balance", "color", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "balance", "created_at", "updated_at")

    def get_balance(self, obj):
        income = obj.transactions.filter(transaction_type=Transaction.TransactionType.INCOME).aggregate_sum if False else None
        from django.db.models import Sum
        income = obj.transactions.filter(transaction_type=Transaction.TransactionType.INCOME).aggregate(total=Sum("amount"))["total"] or 0
        expenses = obj.transactions.filter(transaction_type=Transaction.TransactionType.EXPENSE).aggregate(total=Sum("amount"))["total"] or 0
        incoming = obj.incoming_transfers.aggregate(total=Sum("amount"))["total"] or 0
        outgoing = obj.transactions.filter(transaction_type=Transaction.TransactionType.TRANSFER).aggregate(total=Sum("amount"))["total"] or 0
        return obj.opening_balance + income - expenses + incoming - outgoing


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name", "category_type", "icon", "color", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source="account.name", read_only=True)
    destination_account_name = serializers.CharField(source="destination_account.name", read_only=True)
    category_name = serializers.CharField(source="category.name", read_only=True)

    class Meta:
        model = Transaction
        fields = ("id", "account", "account_name", "destination_account", "destination_account_name", "category", "category_name", "transaction_type", "description", "amount", "transaction_date", "notes", "created_at", "updated_at")
        read_only_fields = ("id", "user", "account_name", "destination_account_name", "category_name", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        user = request.user
        account = attrs.get("account")
        destination = attrs.get("destination_account")
        category = attrs.get("category")
        transaction_type = attrs.get("transaction_type")
        if account and account.user_id != user.id:
            raise serializers.ValidationError({"account": "Conta não pertence ao usuário autenticado."})
        if destination and destination.user_id != user.id:
            raise serializers.ValidationError({"destination_account": "Conta de destino não pertence ao usuário autenticado."})
        if category and category.user_id != user.id:
            raise serializers.ValidationError({"category": "Categoria não pertence ao usuário autenticado."})
        if transaction_type == Transaction.TransactionType.TRANSFER:
            if not destination:
                raise serializers.ValidationError({"destination_account": "Transferências exigem uma conta de destino."})
            if destination == account:
                raise serializers.ValidationError({"destination_account": "A conta de destino deve ser diferente da origem."})
            if category:
                raise serializers.ValidationError({"category": "Transferências não utilizam categoria."})
        elif destination:
            raise serializers.ValidationError({"destination_account": "Conta de destino só pode ser usada em transferências."})
        elif not category:
            raise serializers.ValidationError({"category": "Receitas e despesas exigem uma categoria."})
        elif category.category_type != transaction_type:
            raise serializers.ValidationError({"category": "O tipo da categoria deve corresponder ao tipo da transação."})
        return attrs
