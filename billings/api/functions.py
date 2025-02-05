from ..models import *
from django.db.models import Sum, Q, Count, F, DateTimeField
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

import pandas as pd
import calendar
import openpyxl

from . import database_query as dq

def CalcServiceTime(today, classification):
    requests = Requisicao.objects.filter(
        data_solicitacao__month=today.month,
        data_solicitacao__year=today.year,
        finalizada=True,
        classification=classification
    )
    
    hours = 0
    if requests.count() > 0:
        for r in requests:
            hours += ServiceTime(r.dh_inicio_atendimento, r.dh_finalizada)
        return (hours / requests.count())
    else:
        return 0
    
def ServiceTime( start_date, end_date ):
    
    start_date_str = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S%z")
    end_date_str = datetime.strftime(end_date, "%Y-%m-%d %H:%M:%S%z")

    inicio = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S%z")
    fim = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S%z") 

    if fim <= inicio:
        return 0
    horas_uteis = 0
    data_atual = inicio
    while data_atual < fim:
        if data_atual.weekday() < 5: 
            horas = fim - data_atual
            horas_uteis += horas.total_seconds() / 3600
        data_atual += timedelta(days=1)

    return horas_uteis

def LargestRequester(today):
    try:
        branchs = Requisicao.objects.filter(
                data_solicitacao__month=today.month,
                data_solicitacao__year=today.year,
            ).values('branch_destino').annotate(
                total=Count('id')
            ).order_by('-total')[:5]
        branchs_ids = [branchs['branch_destino'] for branchs in branchs]
        return Requisicao.objects.filter(
                data_solicitacao__month=today.month,
                data_solicitacao__year=today.year,
                branch_destino__in=branchs_ids
            ).values('branch_destino__name').annotate(
                total=Count('id')
            ).order_by('-total')
    except IndexError:
        return None

def MostRequestedProducts(today):
    try:
        return ItensRequisicao.objects.filter(
            requisicao__data_solicitacao__month=today.month,
            requisicao__data_solicitacao__year=today.year
        ).values('produto__name').annotate(
            total=Count('id')
        ).order_by('-total')[:5]
    except IndexError:
        return None
    
def SincRC():
    CreateProd()
    rec = dq.consultaRc()
    for r in rec:
        rc = Requisicao(
            branch_solicitacao = Branch.objects.get(code=r[0]),
            branch_destino = Branch.objects.get(code=r[1]),
            operador = Operador.objects.get(cod=r[4]),
            dh_aprovacao = r[7],
            nr_solicitacao = r[2],
            data_solicitacao = r[3],
            qtd_itens = r[5],
            justificativa = r[6],
        )
        if not Requisicao.objects.filter(
                    nr_solicitacao=r[2],
                    branch_solicitacao = Branch.objects.get(code=r[0]),
                    branch_destino = Branch.objects.get(code=r[1])).exists():
            rc.save()
            print("RC SALVA")
            itens = dq.consultaItensRc(rc.nr_solicitacao, rc.branch_solicitacao, rc.branch_destino)
            for i in itens:
                item = ItensRequisicao(
                    requisicao = rc,
                    produto = Produtos.objects.get(code=i[1]),
                    qtd = i[2],
                    dt_utiliza = i[3]
                )
                item.save()
                print("Item Atualizado")
        ClassRequisition()

def ClassRequisition():
    rc = Requisicao.objects.order_by('-created_at').first()
    produto = ItensRequisicao.objects.filter(requisicao=rc).first()
    produto = produto.produto.code[0:3]
    
    insumo = [1, 2, 3, 4]
    epi = 866
    outros = [5,6,7,8,9]
    if produto == epi:
        rc.classification = 2
        rc.save()
    elif compare_first_digit(produto,insumo):
        rc.classification = 1
        rc.save()
    else:
        rc.classification = 3
        rc.save()

def compare_first_digit(numero, lista_numeros):
    primeiro_digito_produto = str(numero)[0]
    for num in lista_numeros:
        primeiro_digito_num = str(num)[0]
        if primeiro_digito_produto == primeiro_digito_num:
            return True
    return False

def CreateProd():
    produtos = dq.CriaProdutos()
    for prod in produtos:
        p = Produtos(
            code = prod[1],
            name = prod[2],
            classification = ClassProduto.objects.get(code=prod[0]),
            unidade = prod[3]
        )
        try:    
            if not Produtos.objects.filter(code=prod[1]).exists():
                p.save()
                print("Salvo")
            else:
                print("Ja Existe")
        except Exception as e:
            print(e)

def Graph_By_Type_Purchasing():
    purchase = []
    classification = [{'id': 1, 'name':'Insumo'},{'id': 2, 'name':'EPI'},{'id': 3, 'name':'Outros'}]
    for classifies in classification:
        purchasing = Requisicao.objects.annotate(
            month=TruncMonth('data_solicitacao')
        ).filter(classification=classifies['id']).values('month', 'classification').annotate(
            total=Count('id')
        ).order_by('month', 'classification')
        purchase.append({
            'name': classifies['name'],
            'total': purchasing
        })
    return purchase

def Months_Graph_Purchasing(): 
    months = list(Requisicao.objects.annotate(month=TruncMonth('data_solicitacao')).values_list('month', flat=True).distinct())
    unique_months = set(months)
    months = [month.strftime('%m/%Y') for month in unique_months]
    months = sorted(months, key=Sort_Month_Year)
    return months
    
def Sort_Month_Year(item):
    month, year = item.split('/')  # Divide a string em mês e ano
    return int(year), int(month)   # Retorna uma tupla (ano, mes) para ordenação
    
def Graph_Pie_By_Type_Purchasing():
    today   = datetime.today()
    today   = today.replace(day=1)
    last_day_previous_month = today - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    previous_month = first_day_previous_month.strftime('%Y-%m-%d')
    purchase = []
    classification = [{'id': 1, 'name':'Insumo'},{'id': 2, 'name':'EPI'},{'id': 3, 'name':'Outros'}]
    for classifies in classification:
        purchasing = Requisicao.objects.annotate(
            month=TruncMonth('data_solicitacao')
        ).filter(
            classification=classifies['id'],
            month = previous_month
        ).values('month', 'classification').annotate(
            total=Count('id')
        ).order_by('month', 'classification')
        purchase.append({
            'name': classifies['name'],
            'total': purchasing
        })
    return purchase
    
def Create_Product(code):
    product = dq.Read_And_Create_Product(code)
    p = Produtos(
        code = product[0][1],
        name = product[0][2],
        classification = ClassProduto.objects.get(code=product[0][0]),
        unidade = product[0][3]
    )
    try:    
        if not Produtos.objects.filter(code=product[0][1]).exists():
            p.save()
            print("Salvo")
            return p
        else:
            print("Ja Existe")
    except Exception as e:
        print(e)