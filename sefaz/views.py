from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import BusinessForm
from .models import Business
from sefaz.api.nfe import check_nfe

@login_required
def nfe(request):
    nfe = []
    bss = Business.objects.all()
    for business in bss:
        nfe.append(check_nfe(business))
    print(nfe)
    return render(request, 'pages/nfe.html',{
        'nfe': nfe
    })

@login_required
def business(request):
    bss = Business.objects.all()
    if request.method == 'POST':
        form = BusinessForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            form = BusinessForm()
            return render(request, 'pages/business.html',{'form': form,'business': bss})
    else:
        form = BusinessForm()
    return render(request, 'pages/business.html', {'form': form,'business': bss})