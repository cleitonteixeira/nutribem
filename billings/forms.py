from datetime import datetime
from django import forms
from requests import request
from .models import *

class EndRequestForm(forms.ModelForm):
    status = forms.IntegerField(widget=forms.HiddenInput())
    observation = forms.CharField(
        label='Observações',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control form-control-sm mb-1',
                'rows': 2,
                'cols': 30
            }),
    )
    finalizada = forms.BooleanField(widget=forms.HiddenInput(), initial=True)
    dh_finalizada = forms.DateTimeField(widget=forms.HiddenInput(), initial=datetime.now())
    progress = forms.IntegerField(widget=forms.HiddenInput(), initial=4)
    
    class Meta:
        model = Requisicao
        fields = ['observation','status','finalizada','dh_finalizada','progress']

        
class StartRequestForm(forms.ModelForm):
    
    status = forms.IntegerField(widget=forms.HiddenInput())
    inicio_atendimento = forms.BooleanField(widget=forms.HiddenInput(), initial=True)
    operador_atendimento = forms.ModelChoiceField(queryset=Operador.objects.all(), widget=forms.HiddenInput())
    dh_inicio_atendimento = forms.DateTimeField(widget=forms.HiddenInput(), initial=datetime.now())
   
    class Meta:
        model = Requisicao
        fields = ['status','inicio_atendimento','operador_atendimento','dh_inicio_atendimento']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['operador_atendimento'].initial = user
 