from django.contrib import admin
from .models import *


@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    ...

@admin.register(TypeBranch)
class TypeBranchAdmin(admin.ModelAdmin):
    ...

@admin.register(FinancialClassification)
class FinancialClassificationAdmin(admin.ModelAdmin):
    ...
    
@admin.register(FinancialTransactions)
class FinancialTransactionsAdmin(admin.ModelAdmin):
    ...
    
@admin.register(Cooperators)
class CooperatorsAdmin(admin.ModelAdmin):
    ...

@admin.register(Events)
class EventsAdmin(admin.ModelAdmin):
    ...
    
@admin.register(EventHistory)
class EventHistoryAdmin(admin.ModelAdmin):
    ...

@admin.register(GroupEvents)
class GroupEventsAdmin(admin.ModelAdmin):
    ...

@admin.register(EventsByGroup)
class EventsByGroupAdmin(admin.ModelAdmin):
    ...
    
@admin.register(Operador)
class OperadorAdmin(admin.ModelAdmin):
    ...
    
@admin.register(Requisicao)
class RequisicaoAdmin(admin.ModelAdmin):
    ...

@admin.register(ClassProduto)
class ClassProdutoAdmin(admin.ModelAdmin):
    ...

@admin.register(Produtos)
class ProdutosAdmin(admin.ModelAdmin):
    ...

@admin.register(ItensRequisicao)
class ItensRequisicaoAdmin(admin.ModelAdmin):
    ...