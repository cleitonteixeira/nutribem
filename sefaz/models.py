from django.db import models



class Base(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    class Meta:
        abstract = True

class Business(Base):
    UF_CHOICES = (
        ('MG', 'Minas Gerais'),
        ('SP', 'São Paulo'),
        ('PR', 'Paraná'),
        ('RS', 'Rio Grande do Sul'),
        ('SC', 'Santa Catarina'),
        ('ES', 'Espírito Santo'),
        ('GO', 'Goiás'),
        ('MT', 'Mato Grosso'),
        ('MS', 'Mato Grosso do Sul'),
        ('AC', 'Acre'),
        ('AL', 'Alagoas'),
        ('AP', 'Amapá'),
        ('AM', 'Amazonas'),
        ('BA', 'Bahia'),
        ('CE', 'Ceará'),
        ('DF', 'Distrito Federal'),
        ('ES', 'Espírito Santo'),
        ('MA', 'Maranhão'),
        ('RN', 'Rio Grande do Norte'),
        ('RR', 'Roraima'),
        ('RO', 'Rondônia'),
        ('TO', 'Tocantins'),
        ('PA', 'Pará'),
        ('PB', 'Paraíba'),
        ('PE', 'Pernambuco'),
        ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'),
        ('SE', 'Sergipe'),
    )

    name = models.CharField("Empresa",max_length=100)
    cnpj = models.CharField("CNPJ",max_length=14, unique=True)
    certificate = models.FileField("Certificado",upload_to='certificates/%Y/%m/%d/', default='')
    password = models.CharField("Senha Certificado",max_length=100)
    nsu = models.IntegerField("NSU", default='0')
    uf = models.CharField("UF",max_length=2, choices=UF_CHOICES)
    
    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
    
    def __str__(self):
        return f"{self.name} - {self.cnpj}"