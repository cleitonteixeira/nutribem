from django.shortcuts import render

from .api import sentinel

def home(request):
    dados = sentinel.FindCalls()
    print(dados)
    return render(request, 'pages/index.html', context={
        'dados':dados
    })