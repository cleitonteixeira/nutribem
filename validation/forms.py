
from datetime import datetime
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from requests import request

class MyPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="Senha atual",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        label="Nova senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="""
                <ul>
                    <li>Sua senha não pode ser muito parecida com o resto das suas informações pessoais.</li>
                    <li>Sua senha precisa conter pelo menos 8 caracteres.</li>
                    <li>Sua senha não pode ser uma senha comumente utilizada.</li>
                    <li>Sua senha não pode ser inteiramente numérica.</li>
                </ul>
                        """
    )
    new_password2 = forms.CharField(
        label="Confirmação",
        widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':"Repita a nova senha"})
    )
    
class LoginForm(forms.Form):
    username = forms.CharField(label="Usuário:", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':"Nome de usuário"}))
    password = forms.CharField(label="Senha:",widget=forms.PasswordInput(attrs={'class': 'form-control','placeholder':"Senha"}))

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise forms.ValidationError("Nome de usuário ou senha inválidos.")
        return cleaned_data

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(label="Nome", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Sobrenome", max_length=100,widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="E-mail",widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']