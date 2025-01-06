from .models import FinancialTransactions
from django.db.models import Sum, FloatField, Value
from django.db.models.functions import Coalesce
def getRevenueTotalBranch(date,branch):
    revenue = FinancialTransactions.objects.filter(
        period = date.strftime("%m/%Y"),
        branch__code = branch,
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS','LOCACAO DE BENS','PROVISAO DE RECEITAS']
    ).values('branch__code').annotate(
        total=Coalesce(Sum('value'),0.0, output_field=FloatField())
    )
    return revenue
def getRevenueTotalType(date,type,branch):
    revenue = FinancialTransactions.objects.filter(
        period = date.strftime("%m/%Y"),
        branch__code = branch,
        type = type
    ).values('branch__code').annotate(
        total=Coalesce(Sum('value'),0.0,output_field=FloatField())
    )
    return revenue