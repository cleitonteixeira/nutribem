from django.shortcuts import render,redirect
from django.template.loader import get_template
from django.db.models import Sum, Q, Count
from django.db.models.functions import TruncMonth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from datetime import date ,datetime, timedelta
from .models import *
from .forms import *

from .api import functions as fc
from .api import database_query as dq

import pandas as pd
import calendar
import openpyxl

from . import completaBD
from . import completDRE
from . import attBanco

def ExpenseDataCreate(data):
    print (data)
    register = []
    data_cr = []
    for mesano,cr,valor,descricao in data:
        register_cr = {
            'cr': cr,
            'mesano': mesano,
        }
        data_cr.append(register_cr)
    
    data_cr = pd.DataFrame(data_cr)
    data_cr = data_cr.drop_duplicates(subset=['cr','mesano'])
    data_cr = data_cr.values.tolist()
    for register_cr in data_cr:
        register.append(
                {
                    'cr': register_cr[0],
                    'mesano': register_cr[1],
                    'despesas': [
                        {
                            'ADMINISTRATIVO': 0
                        },{
                            'PESSOAS': 0
                        },{
                            'INSUMOS': 0
                        },{
                            'OUTROS': 0
                        }
                    ],
                }
        )
        
    for mesano,cr,valor,descricao in data:
        atualizar_despesa(register, cr, mesano, descricao, valor)
    register = ordenar_despesas(register)
    return register


def setValuesBD():
    values = completaBD.consulta()
    for value in values:
        print(value)

def ordenar_despesas(despesas):
    return sorted(despesas, key=lambda x: (x['cr']))

def atualizar_despesa(despesas, cr, mesano, tipo_despesa, novo_valor):
    for registro in despesas:
        if registro['cr'] == cr:
            if registro['mesano'] == mesano:
                for despesa in registro['despesas']:
                    if tipo_despesa in despesa:
                        despesa[tipo_despesa] = novo_valor*(-1)
                        return  # Sai do loop se encontrou e atualizou

def getExpenses(id,date):
    tExpenses = []
    expenses = FinancialTransactions.objects.filter(
        branch__id=id.id,
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    )
    for expense in expenses:
        percent = getValueExpensePercent(id,date,expense.type)
        exs = {
                'type': expense.type,
                'value': expense.value*(-1),
                'percent': percent
            }
        tExpenses.append(exs)
    return tExpenses
    
def getBranch(code):
    branch = Branch.objects.get(code=code)
    return branch

def getValueExpensePercent(id,date,type):
    month = calcMonth(date).strftime("%Y-%m")
    lastValue =  getValueEspense(id,month,type).first()
    if lastValue:
        lastValue = lastValue.value
    else:
        lastValue = 0
    atualValue = getValueEspense(id,date,type).first().value
    if lastValue != 0:
        percent = calc_percent(
                atualValue,
                lastValue
            )
    else:
        percent = 0
    return percent

def getValueExpensePercentMonth(date,type):
    month = calcMonth(date.strftime("%Y-%m"))
    lastValue =  getValueExpenseTypeSum(month,type)
    if lastValue:
        lastValue = lastValue
    else:
        lastValue = 0
    atualValue = getValueExpenseTypeSum(date,type)
    if lastValue != 0:
        percent = calc_percent(
                atualValue[0]['value'],
                lastValue[0]['value']
            )
    else:
        percent = 0
    return percent

def getValueEspense(id,date,type):
    expense = FinancialTransactions.objects.filter(
        branch__id=id.id,
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type = type
    )
    return expense

def getValueExpenseType(date,type):
    expense = FinancialTransactions.objects.filter(
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type = type
    )
    return expense

def getValueExpenseTypeSum(date,type):
    expense = FinancialTransactions.objects.filter(
        period = date.strftime("%m/%Y"),
        type = type
    ).values('type').annotate(
        value=-Sum('value'))
    return expense

def getTotalExpensesForBranch(id,date):
    expenses = FinancialTransactions.objects.filter(
        branch__id=id.id,
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('period').annotate(
        value=-Sum('value'))
    return expenses

def getTotalExpensesMonth(id):
    months = last6Months()
    expenses = FinancialTransactions.objects.filter(
        branch__id=id.id,
        period__in=months,
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('period').annotate(
        total=-Sum('value')
    ).order_by('period')[:6]
    return expenses

def getTotalExpensesTypeMonth(id):
    months = last6Months()
    expenses = FinancialTransactions.objects.filter(
        branch__in=id,
        period__in=months,
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('period').annotate(
        total=-Sum('value')
    ).order_by('period')[:6]
    return expenses

def getTotalExpensesEnterprise(data):
    today = data.strftime("%m/%Y")
    expenses = FinancialTransactions.objects.filter(
        period=today,
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('period','type').annotate(
        value=-Sum('value')
    )
    tExpenses = []
    
    for expense in expenses:
        percent = getValueExpensePercentMonth(data,expense['type'])
        exs = {
                'type': expense['type'],
                'value': expense['value'],
                'percent': percent
            }
        tExpenses.append(exs)
    return tExpenses

def defExpensesWithMonth(date):
    expenses = FinancialTransactions.objects.filter(
        period = date
    )
    expenses.delete()
    print ("Removidas")
    return expenses

def getTotalExpensesWithType():
    months = last6Months()
    expenses = FinancialTransactions.objects.filter(period__in=months, type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']).values('period','type').annotate(
        total=-Sum('value')
    ).order_by('period')
    
    return expenses

def last6Months():
    today = datetime.now()
    months = []
    months.append(today.strftime("%m/%Y"))
    previous_month = today.replace(day=1) - timedelta(days=1)
    for _ in range(5):
        previous_month -= timedelta(days=28)
        months.append(previous_month.strftime("%m/%Y"))
    return months[::-1]

def calcMonth(nMonth):
    pMonth = datetime.strptime(nMonth, "%Y-%m")
    if pMonth.month == 1:
        previous_year = pMonth.year - 1
        previous_month = 12
    else:
        previous_year = pMonth.year
        previous_month = pMonth.month - 1
    lDay = calendar.monthrange(previous_year, previous_month)[1]
    oneMonth = timedelta(days=lDay)
    pMonth = pMonth - oneMonth
    return pMonth

def calc_percent (last,second_last):
    if second_last > 0:
        v_final = last/second_last
        v_final = (v_final-1)*100
        v_final = round(v_final,2)
        return v_final
    else:
        return 0

@login_required
def home (request):
    return render(request, 'pages/home.html')

def invoices (request):
    data = datetime.now()
    return render(request, 'pages/invoices.html', context={
        'data':data,
        'invoices': 'a'
    })

def invoice (request, id):
    return render(request, 'pages/invoice.html')

def costs(request):
    data = calcMonth(datetime.now().strftime("%Y-%m"))    
    if request.POST.get('data') is not None:
        data = datetime.strptime(request.POST.get('data'), '%Y-%m') 
    
    return render(request, 'pages/costs.html', context={
        'expenseWithType': getTotalExpensesWithType(),
        'months': last6Months(),
        'resultMonth' : getTotalExpensesEnterprise(data),
        'data': data
    })

def getTotalRevenueDate(date):
    revenue = FinancialTransactions.objects.filter(
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS']
    ).values('period').annotate(
        total=Sum('value')
    )
    return revenue

def getPercentRevenue(date):
    lastValue = getTotalRevenueDate(calcMonth(date).strftime("%Y-%m"))
    if lastValue:
        lastValue = lastValue[0]['total']
        atualValue = getTotalRevenueDate(date)
        atualValue = atualValue[0]['total']
        percent = calc_percent(
                atualValue,
                lastValue
            )
    else:
        percent = 0
    return percent

def getRevenueListMonth():
    months = last6Months()
    revenue = FinancialTransactions.objects.filter(
        period__in=months,
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS']
    ).values('period').annotate(
        total=Sum('value')
    ).order_by('period')[:6]
    return revenue

def getRevenueListType():
    months = last6Months()
    revenue = FinancialTransactions.objects.filter(
        period__in=months,
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS']
    ).values('type','period').annotate(
        total=Sum('value')
    )
    return revenue

def getItensDRE(date):
    itens =  FinancialTransactions.objects.filter(
        branch__in = Branch.objects.filter(~Q(type__id=1)),
        period = date.strftime("%m/%Y")
    ).values('period','branch__code','type').annotate(
        total=Sum('value')
    ).order_by('branch__code','type')
    return itens
    
def getBranchUsed(date):
    branchs = FinancialTransactions.objects.filter(
        period = date.strftime("%m/%Y"),
        branch__in = Branch.objects.filter(~Q(type__id=1))
    ).values('branch','branch__code').distinct()
    return branchs

def getValuesDRE(date):
    cr = getBranchUsed(date)
    values = []
    for cr in cr:
        value = {
            'branch': cr['branch__code'],
            'Receita_Bruta': completDRE.getRevenueTotalBranch(date,cr['branch__code'])
                if completDRE.getRevenueTotalBranch(date,cr['branch__code']) else [{'branch__code':cr['branch__code']},{'total':'0.00'}],
            'Revenda_de_Mercadorias': completDRE.getRevenueTotalType(date,'REVENDA DE PRODUTOS',cr['branch__code']) 
                if completDRE.getRevenueTotalType(date,'REVENDA DE PRODUTOS',cr['branch__code']) else [{'branch__code':cr['branch__code']},{'total':'0.00'}],
            'Vendas_de_Produtos': completDRE.getRevenueTotalType(date,'VENDA DE PRODUTOS',cr['branch__code'])
                if completDRE.getRevenueTotalType(date,'VENDA DE PRODUTOS',cr['branch__code']) else [{'branch__code':cr['branch__code']},{'total':'0.00'}],
            'Vendas_de_Servicos': completDRE.getRevenueTotalType(date,'VENDA DE SERVICOS',cr['branch__code'])
                if completDRE.getRevenueTotalType(date,'VENDA DE SERVICOS',cr['branch__code']) else [{'branch__code':cr['branch__code']},{'total':'0.00'}],
            'Locacao_de_Bens': completDRE.getRevenueTotalType(date,'LOCACAO DE BENS',cr['branch__code'])
                if completDRE.getRevenueTotalType(date,'LOCACAO DE BENS',cr['branch__code']) else [{'branch__code':cr['branch__code']},{'total':'0.00'}],
            'Provisoes_de_Receitas': completDRE.getRevenueTotalType(date,'PROVISAO DE RECEITAS',cr['branch__code'])
                if completDRE.getRevenueTotalType(date,'PROVISAO DE RECEITAS',cr['branch__code']) else [{'branch__code':cr['branch__code']},{'total':'0.00'}],
        }
        values.append(value)
    return values

def dre(request):
    data = calcMonth(datetime.now().strftime("%Y-%m"))
    if request.POST.get('data') is not None:
        data = datetime.strptime(request.POST.get('data'), '%Y-%m')
        return render(request, 'pages/dre.html',context={
            'crs' : getBranchUsed(data),
            'itens': getItensDRE(data),
            'dre':getValuesDRE(data),
            'data': data
        })
    else:
        return render(request, 'pages/dre.html',context={
            'crs' : getBranchUsed(data),
            'itens': getItensDRE(data),
            'dre':getValuesDRE(data),
            'data': data
        })

def expenses_cr(request):
    if request.POST.get('cr_select') is not None:
        data = datetime.strptime(request.POST.get('data'), '%Y-%m')
        return render(request, 'pages/expenses_cr.html',context={
            'crs' : Branch.objects.all(),
            'cResult': getBranch(request.POST.get('cr_select')),
            'results': getExpenses(getBranch(request.POST.get('cr_select')),request.POST.get('data')),
            'total': getTotalExpensesForBranch(getBranch(request.POST.get('cr_select')),request.POST.get('data')),
            'resultMonth':getTotalExpensesMonth(getBranch(request.POST.get('cr_select'))),
            'data': data
        })
    else:
        return render(request, 'pages/expenses_cr.html',context={
            'crs' : Branch.objects.all()
        })
        
def SincOperador():
    operador = attBanco.consultaOperador()
    for op in operador:
        if not Operador.objects.filter(cod=op[0]).exists():
            Operador.objects.create(cod=op[0],name=op[1])
            print("Salvo")
        else:
            Operador.objects.filter(cod=op[0]).update(name=op[1])
            print("Atualizado")

def SincBranch():
    filiais = attBanco.consultaFiliais()
    for fil in filiais:
        if not Branch.objects.filter(code=fil[0]).exists():
            Branch.objects.create(code=fil[0],name=fil[1])
            print("Salvo")
        else:
            Branch.objects.filter(code=fil[0]).update(name=fil[1])
            print("Atualizado")
    
def synchronization(request):
    date = datetime.now()
    if request.POST.get('sinc') == 'sinc_eventos':
        SincEvents(request.FILES['file'])
        return render(request, 'pages/synchronization.html', context={
            'crs' : Branch.objects.all(),
            'date': date
        })
    elif request.POST.get('operador') == 'sincronize':
        SincOperador()
        return render(request, 'pages/synchronization.html', context={
            'date': date
        })
    elif request.POST.get('rc') == 'sincronize':
        SincRC()
        return render(request, 'pages/synchronization.html', context={
            'date': date
        })
    elif request.POST.get('filial') == 'sincronize':
        SincBranch()
        return render(request, 'pages/synchronization.html', context={
            'date': date
        })
    elif request.POST.get('produto') == 'sincronize':
        CreateProd()
        return render(request, 'pages/synchronization.html', context={
            'date': date
        })
    elif request.POST.get('sinc') == 'sinc_colaborador':
        SincColaborador(request.FILES['file'])
        return render(request, 'pages/synchronization.html', context={
            'crs' : Branch.objects.all(),
            'date': date
        })
    elif request.POST.get('sinc') == 'sinc_ctbl':
        date = datetime.strptime(request.POST.get('data'), '%Y-%m')
        dados = completaBD.consulta(date.strftime("%m/%Y"))
        defExpensesWithMonth(date.strftime("%m/%Y"))
        for dado in dados:
            saveFinancialTransactions(dado)
        return render(request, 'pages/synchronization.html', context={
            'crs' : Branch.objects.all(),
            'date': date
        })
    elif request.POST.get('sinc') == 'sinc_history_events':
        eventos = SincHistoryEvents(request.FILES['file'])
        return render(request, 'pages/synchronization.html', context={
            'crs' : Branch.objects.all(),
            'date': date,
            'eventos': eventos
        })
    elif request.POST.get('sinc') == 'del_history_events':
        EventHistory.objects.all().delete()
        return render(request, 'pages/synchronization.html', context={
            'crs' : Branch.objects.all(),
            'date': date,
            'del': "Historico Removido"
        })
    else:
        return render(request, 'pages/synchronization.html', context={
            'crs' : Branch.objects.all(),
            'date': date
        })
        
def CreateProd():
    produtos = dq.CriaProdutos()
    if produtos is not None:
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
        
def ConvertDate(date):
    print(date)
    try:
        return datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def ConvertDateTime(date):
    print(date)
    try:
        return datetime.strptime(date, "%d/%m/%Y %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return None

def getBranch(code):
    try:
        return Branch.objects.get(code=code)
    except Exception as e:
        return None

def getCooperator(link):
    try:
        return Cooperators.objects.get(link=link)
    except Exception as e:
        return None

def SincColaborador(file):
    df = pd.read_excel(file)
    lista = df.values.tolist()
    for l in lista:
        code = l[12][0:4]
        colab = Cooperators(
            name = l[3],
            cpf = l[4].replace('.','').replace('-',''),
            admission = datetime.strptime(l[6], "%d/%m/%Y").strftime("%Y-%m-%d"),
            ocupation = l[10],
            birthdate = datetime.strptime(l[8], "%d/%m/%Y").strftime("%Y-%m-%d"),
            cod = l[1],
            link = l[0],
            type = l[5],
            sex = l[9],
            branch = getBranch(code),
            demission = ConvertDate(l[7]),
            situation = l[11]
        )
        if not Cooperators.objects.filter(link = l[0]).exists():
            try:
                colab.save()
                print("Salvo")
            except Exception as e:
                print(e)
        else:
            colaborador = Cooperators.objects.get(link = l[0])
            colaborador.name = l[3]
            colaborador.ocupation = l[10]
            colaborador.branch =  getBranch(code)
            colaborador.demission = ConvertDate(l[7])
            colaborador.situation = l[11]
            try:
                colaborador.save()
                print("Registro Atualizado")
            except Exception as e:
                print(e)
    
def SincEvents(file):
    df = pd.read_excel(file)
    lista = df.values.tolist()
    for l in lista:
        event = Events(
            cod = l[0],
            name = l[1],
            typeEvent = l[2],
            demonstrative = l[3] == "Sim"
        )
        try:
            event.save()
            print("Salvo")
        except Exception as e:
            print(e)

def getEvent(cod):
    try:
        return Events.objects.get(cod=cod)
    except Exception as e:
        return None

def history(request):
    return render(request, 'pages/history.html',context={
        'eventos': request.session.get('eventos')
    })

def SincHistoryEvents(file):
    event_error = []
    cont = 0
    falha = 0
    df = pd.read_excel(file)
    lista = df.values.tolist()
    for l in lista:
        event = EventHistory(
            cooperator = getCooperator(l[0]),
            event = getEvent(l[9]),
            competence = ConvertDate(l[26]),
            movement = l[11],
            occurrence = ConvertDate(l[16]),
            valuereference = l[13],
            value = l[14]
        )
        try:
            if not EventHistory.objects.filter(
                    cooperator = getCooperator(l[0]),
                    event = getEvent(l[9]),
                    movement = l[11],
                    competence = ConvertDate(l[16]),
                    value = l[14]
                ).exists():
                event.save()
                cont += 1
                print("Salvo")
            else:
                event_error.append(event)
                falha += 1
                print("Ja Existe")
        except Exception as e:
            event_error.append(event)
            falha += 1
    retorno = {
        'cont': cont,
        'falha': falha,
        'event_error': event_error
    }
    return retorno

def saveFinancialTransactions(data):
    if Branch.objects.filter(code=data[1]).exists():
        branch = Branch.objects.get(code=data[1])
        ftData = FinancialTransactions(
            type = data[3],
            value = data[2],
            period = data[0],
            branch_id = branch.id
        )
        if not FinancialTransactions.objects.filter(type = data[3], period = data[0], branch_id = branch.id).exists():
            ftData.save()
            print("Salvo")
        else:
            print("Ja Existe")
    return

def expenses_type(request):
    if request.POST.get('class_select') is not None:
        data = datetime.strptime(request.POST.get('data'), '%Y-%m')
        return render(request, 'pages/expense_type.html',context={
            'types' : TypeBranch.objects.all(),
            'cResult': getTypeBranch(request.POST.get('class_select')),
            'results': getExpensesWithType(getBranchWithType(request.POST.get('class_select')),request.POST.get('data')),
            'total': getTotalExpensesForType(getBranchWithType(request.POST.get('class_select')),request.POST.get('data')),
            'resultMonth':getTotalExpensesTypeMonth(getBranchWithType(request.POST.get('class_select'))),
            'data': data
        })
    else:
        return render(request, 'pages/expense_type.html',context={
            'types' : TypeBranch.objects.all()
        })
        
def getBranchWithType(id):
    branch = Branch.objects.filter(type__id=id).all()
    return branch

def getTypeBranch(id):
    type = TypeBranch.objects.get(id=id)
    return type

def getExpensesWithType(branch,date):
    tExpenses = []
    expenses = FinancialTransactions.objects.filter(
        branch__in=branch,
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('type').annotate(
        value=-Sum('value')
    )    
    for expense in expenses:
        percent = getValueExpensePercentWithType(branch,date,expense['type'])
        exs = {
                'type': expense['type'],
                'value': expense['value'],
                'percent': percent
            }
        tExpenses.append(exs)
    return tExpenses
    
def getValueExpensePercentWithType(branch,date,type):
    percent = 0
    month = calcMonth(date).strftime("%Y-%m")
    lastValue =  getValueExpenseWithType(branch,month,type)
    if lastValue:
        lastValue = lastValue[0]['value']
        atualValue = getValueExpenseWithType(branch,date,type)[0]['value']
        percent = calc_percent(
                atualValue,
                lastValue
            )

    return percent

def getValueExpenseWithType(branch,date,type):
    expense = FinancialTransactions.objects.filter(
        branch__in=branch,
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type = type
    ).values('type').annotate(
        value=-Sum('value')
    )
    return expense

def getTotalExpensesForType(branch,date):
    expenses = FinancialTransactions.objects.filter(
        branch__in=branch,
        period = datetime.strptime(date, "%Y-%m").strftime("%m/%Y"),
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('period').annotate(
        value=-Sum('value'))
    return expenses

def getTotalExpensesMonthType(branch):
    months = last6Months()
    expenses = FinancialTransactions.objects.filter(
        branch__in=branch,
        period__in=months,
        type__in=['ADMINISTRATIVO','INSUMOS','PESSOAS']
    ).values('period').annotate(
        total=-Sum('value')
    ).order_by('period')[:6]
    return expenses

def HoraExtras(request):
    return render(request, 'pages/hora_extra.html',context={
        "value": getSumByGroup()
    })
    
def lastSixMonths():
    today = datetime.now()
    today = today.replace(day=1)
    months = []
    months.append(today.strftime("%Y-%m-%d"))
    previous_month = today.replace(day=1) - timedelta(days=1)
    for _ in range(5):
        previous_month -= timedelta(days=28)
        previous_month = previous_month.replace(day=1)
        months.append(previous_month.strftime("%Y-%m-%d"))
    return months[::-1]

def getSumByGroup():
    month = lastSixMonths()
    grupos = GroupEvents.objects.all()
    dados = []
    for grupo in grupos:
        events = EventsByGroup.objects.filter(
            group = grupo
        )
        event_id = events.values_list('event', flat=True)
        value = EventHistory.objects.filter(
            event__id__in=event_id,
            competence__in=month
        ).values('competence').annotate(total=Sum('value'))
        dados.append({
            'name': grupo,
            'values': value
            })
    return dados

def groupEvents(request):
    if request.POST.get('save') is not None:
        name = request.POST.get('group')
        return render(request, 'pages/group_events.html',context={
            "response": setGroupEvents(name),
            "groups": GroupEvents.objects.all()
        })
    elif request.POST.get('action') == "remove":
        response = delGroupEvents(request.POST.get('id'))
        return render(request, 'pages/group_events.html',context={
            "groups": GroupEvents.objects.all(),
            "response": response
        })
    elif request.POST.get('action') == "edit":
        return render(request, 'pages/group_events.html',context={
            "groups": GroupEvents.objects.all(),
            "response": HttpResponse(content="Editar", status=200)
        })
    elif request.POST.get('action') == "list":
        listEventos = getEventsNotByGroup()
        eventos = listGroupEvents(request.POST.get('id'))
        grupo = getGroupEvents(request.POST.get('id'))
        return render(request, 'pages/group_events.html',context={
            "groups": GroupEvents.objects.all(),
            "eventos": eventos,
            "listEventos":listEventos,
            "list": True,
            "grupo": grupo,
            "response": HttpResponse(content="Listado", status=200)
        })
    elif request.POST.get('listaGrupo') == "salvar":
        setEventosInGroup(request.POST.get('grupo_id'),request.POST.getlist('eventos[]'))        
        listEventos = getEventsNotByGroup()
        eventos = listGroupEvents(request.POST.get('grupo_id'))
        grupo = getGroupEvents(request.POST.get('grupo_id'))
        return render(request, 'pages/group_events.html',context={
            "groups": GroupEvents.objects.all(),
            "eventos": eventos,
            "listEventos":listEventos,
            "list": True,
            "grupo": grupo,
            "response": HttpResponse(content="Listado", status=200)
        })
    elif request.POST.get('listaGrupo') == "remover":
        delEventsByGroup(request.POST.get('idGrupo'))
        listEventos = getEventsNotByGroup()
        eventos = listGroupEvents(request.POST.get('grupo_id'))
        grupo = getGroupEvents(request.POST.get('grupo_id'))
        return render(request, 'pages/group_events.html',context={
            "groups": GroupEvents.objects.all(),
            "eventos": eventos,
            "listEventos":listEventos,
            "list": True,
            "grupo": grupo,
            "response": HttpResponse(content="Listado", status=200)
        })
    else:
        return render(request, 'pages/group_events.html',context={
            "groups": GroupEvents.objects.all(),
            "response": HttpResponse(content="Success", status=200)
        })

def delEventsByGroup(id):
    if EventsByGroup.objects.filter(id=id).exists():
        EventsByGroup.objects.filter(id=id).delete()
        return HttpResponse(content="Removido", status=204)
    else:
        return HttpResponse(content="Error: not found", status=400)

def setEventosInGroup(grupo,eventos):
    for evento in eventos:
        e = Events.objects.get(id=evento)
        g = GroupEvents.objects.get(id=grupo)
        ebg = EventsByGroup(
            group = g,
            event = e
        )
        try:
            ebg.save()
            print("Salvo")
        except Exception as e:
            print(e)
def getEventsNotByGroup():
    exclude = EventsByGroup.objects.all()
    exclude = exclude.values_list('event_id', flat=True)
    eventos = Events.objects.filter(~Q(id__in=exclude))
    return eventos

def listGroupEvents(id):
    eventos = EventsByGroup.objects.filter(group=GroupEvents.objects.get(id=id))
    return eventos

def getGroupEvents(id):
    group = GroupEvents.objects.get(id=id)
    return group

def delGroupEvents(id):
    if GroupEvents.objects.filter(id=id).exists():
        group = GroupEvents.objects.filter(id=id)
        group.delete()
        return HttpResponse(content="Removido", status=204)
    else:
        return HttpResponse(content="Error: not found", status=400)

def setGroupEvents(name):
    group = GroupEvents(
        name = name
    )
    if not GroupEvents.objects.filter(name = name).exists():
        try:
            group.save()
            reponse = HttpResponse("Salvo", status=201)
            return reponse
        except Exception as e:
            reponse = HttpResponse("Erro:"+ e, status=400)
            return reponse
    else:
        reponse = HttpResponse("Já existe", status=400)
        return reponse

@login_required
def dashboard_financial(request):
    date = calcMonth(datetime.now().strftime("%Y-%m"))
    if request.POST.get('iDate') is not None:
        date = datetime.strptime(request.POST.get('iDate'), '%Y-%m')
        return render(request, 'pages/dashboard_financial.html', context={
            'fTotal': getFaturamento(date),
            'cTotal': getCustos(date),
            'data': date,
            'billingHistory': getBillingHistory(),
            'billingType': getBillingType(date),
            'totalRevenue': getTotalRevenue(monthsYear()),
            'variationYear':variationYear(monthsYear()),
            'tributos': getTributos(date),
            'variation':variation(date),
            'segmentacao': getBillingTypeSeg()
        })
    else:
        return render(request, 'pages/dashboard_financial.html', context={
            'fTotal': getFaturamento(date),
            'cTotal': getCustos(date),
            'data': date,
            'billingHistory': getBillingHistory(),
            'billingType': getBillingType(date),
            'variation':variation(date),
            'totalRevenue': getTotalRevenue(monthsYear()),
            'variationYear':variationYear(monthsYear()),
            'tributos': getTributos(date),
            'segmentacao': getBillingTypeSeg()
        })

def variation(date):
    variation = []
    pMonth = calcMonth(date.strftime("%Y-%m"))
    pMonth = getFaturamento(pMonth)
    aMonth = getFaturamento(date)
    variation.append({
        'month': calcMonth(date.strftime("%Y-%m")),
        'value':calc_percent(aMonth[0]['total'], pMonth[0]['total'])
    })
    return variation

def pYear(months):
    pYear = datetime.now().year
    pYear = pYear - 1
    pMonths = []
    for month in months:
        month, year = month.split('/')
        date = datetime.strptime(f"{month}/{pYear}", "%m/%Y")
        pMonths.append(date.strftime("%m/%Y"))
    return pMonths

def variationYear(months):
    variation = []
    pYear1 = pYear(months)
    pYears = getTotalRevenue(pYear1)
    aYears = getTotalRevenue(months)
    pYear2 = datetime.now().year
    pYea2r = pYear2 - 1
    variation.append({
        'year': pYea2r,
        'value':calc_percent(aYears['total'], pYears['total'])
    })
    return variation

def monthsYear():
    today = datetime.now()
    firstMonth = today.replace(month=1)
    firstMonth = firstMonth.replace(day=1)
    months = []
    months.append(firstMonth.strftime("%m/%Y"))
    for _ in range(11):
        firstMonth += timedelta(days=31)
        months.append(firstMonth.strftime("%m/%Y"))
    return months

def getTotalRevenue(months):
    receita = FinancialTransactions.objects.filter(
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS','VENDAS CANCELADAS'],
        period__in=months
    ).aggregate(total=Sum('value'))
    return receita

def getNetRevenue(date):
    receita = getFaturamento(date)
    custos = getCustos(date)
    return receita[0]['total'] - custos[0]['total']

def getFaturamento(date):
    faturamento = FinancialTransactions.objects.filter(
        period = date.strftime("%m/%Y"),
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS','VENDAS CANCELADAS']
    ).values('period').annotate(total=Sum('value'))
    if faturamento:
        return faturamento
    else:
        faturamento = [{'period': date, 'total': 0}]
        return faturamento

def getCustos(date):
    custos = FinancialTransactions.objects.filter(
        ~Q(type__in = ['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS']),
        period = date.strftime("%m/%Y")
    ).values('period').annotate(total=-Sum('value'))
    return custos

def getTributos(date):
    print(date)
    tributos = FinancialTransactions.objects.filter(
        type__in = ['IMPOSTOS'],
        period = date.strftime("%m/%Y")
    ).values('period').annotate(total=-Sum('value'))
    return tributos

def getBillingHistory():
    month = last6Months()
    faturamento = FinancialTransactions.objects.filter(
        type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS','VENDAS CANCELADAS'],
        period__in=month
    ).values('period').annotate(total=Sum('value'))
    faturamento = sorted(faturamento, key=lambda x: extract_month_year(x['period']))
    return faturamento

def extract_month_year(period_str):
    """Extracts month and year from the given period string."""
    try:
        month, year = map(int, period_str.split('/'))
        return datetime(year, month, 1)  # Create a datetime object for consistent sorting
    except ValueError:
        return datetime.max  # Handle invalid periods by placing them at the end

def getExpenseHistory():
    month = last6Months()
    despesas = FinancialTransactions.objects.filter(
        ~Q(type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS']),
        period__in=month
    ).values('period').annotate(total=-Sum('value'))
    return despesas

def getBillingType(date):
    billing = []
    type = TypeBranch.objects.filter(
        ~Q(name='BackOffice')
    )
    for t in type:
        branchs = Branch.objects.filter(
            type = t
        )
        branch_id = branchs.values_list('id', flat=True)
        faturamento = FinancialTransactions.objects.filter(
            type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS','VENDAS CANCELADAS'],
            period = date.strftime("%m/%Y"),
            branch__in=branch_id
        ).aggregate(total=Sum('value'))
        billing.append({
            'name': t.name,
            'total': faturamento['total']
        })
    return billing

def getBillingTypeSeg():
    month = last6Months()
    billing = []
    type = TypeBranch.objects.filter(
        ~Q(name='BackOffice')
    )
    for t in type:
        branchs = Branch.objects.filter(
            type = t
        )
        branch_id = branchs.values_list('id', flat=True)
        faturamento = FinancialTransactions.objects.filter(
            type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS'],
            period__in = month,
            branch__in=branch_id
        ).values('period').annotate(total=Sum('value'))
        billing.append({
            'name': t.name,
            'total': faturamento
        })
    return billing

def getExpenseType(date):
    expense = []
    type = TypeBranch.objects.all()
    for t in type:
        branchs = Branch.objects.filter(
            type = t
        )
        branch_id = branchs.values_list('id', flat=True)
        despesas = FinancialTransactions.objects.filter(
            ~Q(type__in=['VENDA DE SERVICOS','VENDA DE PRODUTOS','REVENDA DE PRODUTOS']),
            period = date.strftime("%m/%Y"),
            branch__in=branch_id
        ).aggregate(total=-Sum('value'))
        expense.append({
            'name': t.name,
            'total': despesas['total']
        })
    return expense

@login_required
def requests(request, codigo):
    if codigo == 0:
        return render(request, 'pages/requests_v2.html', context={
            'rq_insumo': Requisicao.objects.filter(
                finalizada=False, classification='1').order_by('dh_aprovacao'),
            'rq_epi': Requisicao.objects.filter(
                finalizada=False, classification='2').order_by('dh_aprovacao'),
            'rq_outros': Requisicao.objects.filter(
                finalizada=False, classification='3').order_by('dh_aprovacao'),
        })
    elif codigo == 1:
        return render(request, 'pages/requests_v2.html', context={
            'rq_insumo': Requisicao.objects.filter(
                finalizada=True, classification='1').order_by('dh_aprovacao'),
            'rq_epi': Requisicao.objects.filter(
                finalizada=True, classification='2').order_by('dh_aprovacao'),
            'rq_outros': Requisicao.objects.filter(
                finalizada=True, classification='3').order_by('dh_aprovacao'),
        })
    
@login_required
def requests_v2(request):
    return redirect('billings:requests')

@login_required
def dashboard_purchasing(request):
    metrics = fc.Graph_By_Type_Purchasing()
    today = datetime.now()
    total_requests_month = Requisicao.objects.filter(
        data_solicitacao__month=today.month,
        data_solicitacao__year=today.year
    ).values('classification').annotate(total=Count('id'))
    hours_insumos = CalcServiceTime(today,1)
    hours_epi = CalcServiceTime(today,2)
    hours_outros = CalcServiceTime(today,3)
    months = fc.Months_Graph_Purchasing()
    requester = LargestRequester(today)
    products = MostRequestedProducts(today)
    metrics_pie = fc.Graph_Pie_By_Type_Purchasing()
    return render(request, 'pages/dashboard_purchasing.html', context={
        'total_requests_month': total_requests_month,
        'hours_insumos': hours_insumos,
        'hours_epi':hours_epi,
        'hours_outros':hours_outros,
        'requester': requester,
        'products': products,
        'metrics':metrics,
        'metrics_pie': metrics_pie,
        'months':months
    })

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
    # Combina data e hora para criar objetos datetime completos

    start_date_str = datetime.strftime(start_date, "%Y-%m-%d %H:%M:%S%z")
    end_date_str = datetime.strftime(end_date, "%Y-%m-%d %H:%M:%S%z")

    inicio = datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S%z")
    fim = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S%z") 

    # Verifica se o intervalo é válido
    if fim <= inicio:
        return 0

    horas_uteis = 0
    data_atual = inicio
    while data_atual < fim:
        if data_atual.weekday() < 5:  # Dias úteis: segunda (0) a sexta (4)
            # Calcula as horas úteis do dia atual, considerando os horários de início e fim
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
    date_rc = date.today()
    date_rc = date_rc - timedelta(days=5)
    date_rc = date_rc.strftime("%d/%m/%Y")
    rec = dq.consultaRc(date_rc)
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
            itens = attBanco.consultaItensRc(rc.nr_solicitacao, rc.branch_solicitacao, rc.branch_destino)
            for i in itens:
                if Produtos.objects.filter(code=i[1]).exists():
                    item = ItensRequisicao(
                        requisicao = rc,
                        produto = Produtos.objects.get(code=i[1]),
                        qtd = i[2],
                        dt_utiliza = i[3]
                    )
                else:
                    item = ItensRequisicao(
                        requisicao = rc,
                        produto = fc.Create_Product(i[1]),
                        qtd = i[2],
                        dt_utiliza = i[3]
                    )   
                item.save()
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

@login_required
def requisition(request, id):
    rc = Requisicao.objects.get(id=id)
    itens = ItensRequisicao.objects.filter(requisicao=id)
    if request.method == 'POST':
        if request.POST.get('status') == "2":
            form = StartRequestForm( request.POST, instance=rc )
            if form.is_valid():
                form.save()
                form = EndRequestForm( initial={'status': '3'},instance=rc )
                return render(request, 'pages/requisition_v2.html',context={
                        'form': form,
                        'requisition': rc,
                        'itens': itens,
                        'detail': True,
                        'label': 'Finalizar Atendimento'
                    })
        elif request.POST.get('status') == "3":
            form = EndRequestForm( request.POST, instance=rc )
            print (form)
            if form.is_valid():
                form.save()
                return render(request, 'pages/requisition_v2.html',context={
                        'requisition': rc,
                        'itens': itens,
                        'detail': True,
                    })
        else:
            return render(request, 'pages/requisition_v2.html', context={
                    'requisition': rc,
                    'itens': itens,
                    'detail': True,
                })
    
    elif rc.inicio_atendimento == False and request.user.groups.filter(name="Comprador").exists():
        form = StartRequestForm(
            initial={
                    'status': '2',
                    'operador_atendimento': Operador.objects.get(user=request.user),
                    'inicio_atendimento':True,
                    'dh_inicio_atendimento':datetime.now(),
                },instance=rc )
        return render(request, 'pages/requisition_v2.html', context={
            'form': form,
            'requisition': rc,
            'itens': itens,
            'detail': True,
            'label': 'Iniciar Atendimento'
        })
    elif rc.inicio_atendimento and not rc.finalizada :
        form = EndRequestForm( 
                initial={
                    'status': '3',
                    'finalizada': True,
                    'dh_finalizada': datetime.now(),
                    'progress': '4'
                    },
                              instance=rc )
        return render(request, 'pages/requisition_v2.html', context={
            'form': form,
            'requisition': rc,
            'itens': itens,
            'detail': True,
            'label': 'Finalizar Atendimento'
        })
    else:
        return render(request, 'pages/requisition_v2.html', context={
            'requisition': rc,
            'itens': itens,
            'detail': True
        })