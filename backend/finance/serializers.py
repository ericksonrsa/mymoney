from datetime import date, timedelta
from django.db.models import Sum
from rest_framework import serializers
from .models import Account, Budget, Category, FinancialGoal, ImportBatch, ImportRow, RecurringTransaction, Transaction

class AccountSerializer(serializers.ModelSerializer):
    balance=serializers.SerializerMethodField()
    class Meta:
        model=Account; fields=("id","name","institution","account_type","opening_balance","balance","color","is_active","created_at","updated_at"); read_only_fields=("id","balance","created_at","updated_at")
    def get_balance(self,obj):
        income=obj.transactions.filter(transaction_type="INCOME").aggregate(total=Sum("amount"))["total"] or 0; expenses=obj.transactions.filter(transaction_type="EXPENSE").aggregate(total=Sum("amount"))["total"] or 0; incoming=obj.incoming_transfers.aggregate(total=Sum("amount"))["total"] or 0; outgoing=obj.transactions.filter(transaction_type="TRANSFER").aggregate(total=Sum("amount"))["total"] or 0
        return obj.opening_balance+income-expenses+incoming-outgoing
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category; fields=("id","name","category_type","icon","color","is_active","created_at"); read_only_fields=("id","created_at")
class TransactionSerializer(serializers.ModelSerializer):
    account_name=serializers.CharField(source="account.name",read_only=True); destination_account_name=serializers.CharField(source="destination_account.name",read_only=True); category_name=serializers.CharField(source="category.name",read_only=True)
    class Meta:
        model=Transaction; fields=("id","account","account_name","destination_account","destination_account_name","category","category_name","transaction_type","description","amount","transaction_date","notes","created_at","updated_at"); read_only_fields=("id","user","account_name","destination_account_name","category_name","created_at","updated_at")
    def validate(self,attrs):
        user=self.context["request"].user; existing=self.instance; account=attrs.get("account",existing.account if existing else None); destination=attrs.get("destination_account",existing.destination_account if existing else None); category=attrs.get("category",existing.category if existing else None); kind=attrs.get("transaction_type",existing.transaction_type if existing else None)
        if account and account.user_id!=user.id: raise serializers.ValidationError({"account":"Conta não pertence ao usuário autenticado."})
        if destination and destination.user_id!=user.id: raise serializers.ValidationError({"destination_account":"Conta de destino não pertence ao usuário autenticado."})
        if category and category.user_id!=user.id: raise serializers.ValidationError({"category":"Categoria não pertence ao usuário autenticado."})
        if kind=="TRANSFER":
            if not destination: raise serializers.ValidationError({"destination_account":"Transferências exigem uma conta de destino."})
            if destination==account: raise serializers.ValidationError({"destination_account":"A conta de destino deve ser diferente da origem."})
            if category: raise serializers.ValidationError({"category":"Transferências não utilizam categoria."})
        elif destination: raise serializers.ValidationError({"destination_account":"Conta de destino só pode ser usada em transferências."})
        elif not category: raise serializers.ValidationError({"category":"Receitas e despesas exigem uma categoria."})
        elif category.category_type!=kind: raise serializers.ValidationError({"category":"O tipo da categoria deve corresponder ao tipo da transação."})
        return attrs
class BudgetSerializer(serializers.ModelSerializer):
    category_name=serializers.CharField(source="category.name",read_only=True); spent=serializers.SerializerMethodField(); remaining=serializers.SerializerMethodField(); percentage=serializers.SerializerMethodField()
    class Meta:
        model=Budget; fields=("id","category","category_name","month","amount","spent","remaining","percentage","notes","created_at","updated_at"); read_only_fields=("id","spent","remaining","percentage","created_at","updated_at")
    def validate(self,attrs):
        category=attrs.get("category",self.instance.category if self.instance else None); month=attrs.get("month",self.instance.month if self.instance else None)
        if category and category.user_id!=self.context["request"].user.id: raise serializers.ValidationError({"category":"Categoria não pertence ao usuário autenticado."})
        if category and category.category_type!="EXPENSE": raise serializers.ValidationError({"category":"Orçamentos devem utilizar categorias de despesa."})
        if month and month.day!=1: raise serializers.ValidationError({"month":"O mês de referência deve usar o primeiro dia do mês."})
        return attrs
    def _spent(self,obj):
        end=(obj.month.replace(day=28)+timedelta(days=4)).replace(day=1); return Transaction.objects.filter(user=obj.user,category=obj.category,transaction_type="EXPENSE",transaction_date__gte=obj.month,transaction_date__lt=end).aggregate(total=Sum("amount"))["total"] or 0
    def get_spent(self,obj): return self._spent(obj)
    def get_remaining(self,obj): return obj.amount-self._spent(obj)
    def get_percentage(self,obj): return round(float(self._spent(obj)/obj.amount*100),2)
class FinancialGoalSerializer(serializers.ModelSerializer):
    percentage=serializers.SerializerMethodField(); remaining=serializers.SerializerMethodField()
    class Meta:
        model=FinancialGoal; fields=("id","name","target_amount","current_amount","percentage","remaining","target_date","notes","is_active","created_at","updated_at"); read_only_fields=("id","percentage","remaining","created_at","updated_at")
    def validate(self,attrs):
        if attrs.get("target_date") and attrs["target_date"]<date.today(): raise serializers.ValidationError({"target_date":"A data da meta não pode estar no passado."})
        return attrs
    def get_percentage(self,obj): return round(min(float(obj.current_amount/obj.target_amount*100),100),2)
    def get_remaining(self,obj): return max(obj.target_amount-obj.current_amount,0)
class RecurringTransactionSerializer(serializers.ModelSerializer):
    account_name=serializers.CharField(source="account.name",read_only=True); category_name=serializers.CharField(source="category.name",read_only=True)
    class Meta:
        model=RecurringTransaction; fields=("id","account","account_name","category","category_name","transaction_type","description","amount","frequency","next_run","end_date","is_active","notes","created_at","updated_at"); read_only_fields=("id","account_name","category_name","created_at","updated_at")
    def validate(self,attrs):
        user=self.context["request"].user; account=attrs.get("account",self.instance.account if self.instance else None); category=attrs.get("category",self.instance.category if self.instance else None); kind=attrs.get("transaction_type",self.instance.transaction_type if self.instance else None); next_run=attrs.get("next_run",self.instance.next_run if self.instance else None)
        if account and account.user_id!=user.id: raise serializers.ValidationError({"account":"Conta não pertence ao usuário autenticado."})
        if category and category.user_id!=user.id: raise serializers.ValidationError({"category":"Categoria não pertence ao usuário autenticado."})
        if kind=="TRANSFER": raise serializers.ValidationError({"transaction_type":"Transferências recorrentes não são suportadas nesta versão."})
        if not category: raise serializers.ValidationError({"category":"Receitas e despesas recorrentes exigem uma categoria."})
        if category.category_type!=kind: raise serializers.ValidationError({"category":"O tipo da categoria deve corresponder ao tipo da transação."})
        if attrs.get("end_date") and next_run>attrs["end_date"]: raise serializers.ValidationError({"end_date":"A data final deve ser igual ou posterior à próxima execução."})
        return attrs
class ImportRowSerializer(serializers.ModelSerializer):
    class Meta:
        model=ImportRow; fields=("id","transaction_date","description","amount","transaction_type","status","error","transaction"); read_only_fields=fields
class ImportBatchSerializer(serializers.ModelSerializer):
    rows=ImportRowSerializer(many=True,read_only=True)
    class Meta:
        model=ImportBatch; fields=("id","account","filename","status","total_rows","imported_rows","created_at","rows"); read_only_fields=("id","filename","status","total_rows","imported_rows","created_at","rows")
    def validate_account(self,value):
        if value.user_id!=self.context["request"].user.id: raise serializers.ValidationError("Conta não pertence ao usuário autenticado.")
        return value
