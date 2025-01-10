from django import forms
from .models import Business


class BusinessForm(forms.ModelForm):
  
    class Meta:
        model = Business
        fields = '__all__'
        widgets = {
            'uf': forms.Select(attrs={'class': 'form-control form-control-sm mb-1 mb-1'}),
            'certificate': forms.FileInput(attrs={'class': 'form-control form-control-sm mb-1', 'accept': '.pfx'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control form-control-sm mb-1'}),
            'nsu': forms.NumberInput(attrs={'class': 'form-control form-control-sm mb-1','min': '0'}),
            'name': forms.TextInput(attrs={'class': 'form-control form-control-sm mb-1'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control form-control-sm mb-1','id': 'id_cnpj','placeholder': '00.000.000/0000-00'}),
        }
        
    def clean_nsu(self):
        nsu = self.cleaned_data['nsu']
        if nsu < 0:
            raise forms.ValidationError('O NSU não pode ser um número negativo.')
        return nsu
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['uf'].empty_label = "Selecione um estado"