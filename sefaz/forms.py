from django import forms
from .models import Business


class BusinessForm(forms.ModelForm):
  
    class Meta:
        model = Business
        fields = '__all__'
        widgets = {
            'uf': forms.Select(attrs={'class': 'form-control form-control-sm'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control form-control-sm', 'accept': '.pfx'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-sm'}),
            'nsu': forms.NumberInput(attrs={'class': 'form-control form-control-sm','min': '0'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control form-control-sm'})
        }
        
    def clean_nsu(self):
        nsu = self.cleaned_data['nsu']
        if nsu < 0:
            raise forms.ValidationError('O NSU não pode ser um número negativo.')
        return nsu
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uf'].empty_label = "Selecione um estado"