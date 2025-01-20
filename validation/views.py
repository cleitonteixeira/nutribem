from django.shortcuts import render,redirect
from django.contrib.auth import update_session_auth_hash, logout, authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import *
# Create your views here.

def LoginView(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect('billings:index')
        else:
            for field_label, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro! {error}')
    else:
        form = LoginForm()
    return render(request, 'pages/login.html', {'form': form})
    
def logoutView(request):
    logout(request)
    return redirect('validation:login')

@login_required
def ChangePassWordView(request):
    if request.method == 'POST':
        form = MyPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Sua senha foi atualizada com sucesso!')
            update_session_auth_hash(request, user)
            return redirect('validation:change_password')
        else:
            for field_label, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro! {error}')
    else:
        form = MyPasswordChangeForm(request.user)
    return render(request, 'pages/change_password.html', {'form': form})

@login_required
def ProfileView(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Seu perfil foi atualizado com sucesso!')
            return redirect('validation:profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Erro no campo {field}: {error}')
    else:
        user = request.user
        form = ProfileForm(instance=request.user)
    return render(request, 'pages/profile.html', {'form': form,'user':user})