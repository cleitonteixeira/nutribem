from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User

class Base(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    
    class Meta:
        abstract = True

class TypeBranch(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'tipos de filiais'
        verbose_name = 'tipo de filial'
    
class Branch(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    type = models.ForeignKey(TypeBranch, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.code} - {self.name} - {self.type}"
    
    class Meta:
        ordering = ['code']
        verbose_name_plural = 'filiais'
        verbose_name = 'filial'

class Supplier(models.Model):
    code = models.CharField(max_length=20, unique=True, null=True)
    name = models.CharField(max_length=50)
    cnpj = models.CharField(max_length=14, unique=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.code} - {self.name} - {self.cnpj}"
    
    class Meta:
        ordering = ['cnpj']
        verbose_name_plural = 'fornecedores'
        verbose_name = 'fornecedor'

class Invoice(models.Model):
    launch_id = models.CharField(max_length=12)
    type = models.CharField(max_length=30)
    value = models.FloatField()
    expiration = models.DateField()
    branch_id = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.branch.code} - {self.supplier.name} - {self.type} - {self.value}"
    
    class Meta:
        ordering = ['launch_id']
        verbose_name_plural = 'notas fiscais'
        verbose_name = 'nota fiscal'

class FinancialTransactions(models.Model):
    type = models.CharField(max_length=30)
    value = models.FloatField()
    period = models.CharField(max_length=7)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.branch.code} - {self.period} - {self.type} - {self.value}"
    
    class Meta:
        ordering = ['period','branch']
        verbose_name_plural = 'transações financeiras'
        verbose_name = 'transação financeira'

class FinancialClassification(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return self.name

class Cooperators(models.Model):
    name = models.CharField("Nome",max_length=50)
    cpf = models.CharField("CPF",max_length=11)
    admission = models.DateField("Admissão")
    ocupation = models.CharField("Cargo",max_length=50)
    birthdate = models.DateField("Data de nascimento")
    cod = models.IntegerField("Matrícula",unique=True)
    link = models.IntegerField("Vínculo",unique=True)
    type = models.CharField("Tipo de Contrato",max_length=30)
    sex = models.CharField("Sexo",max_length=30,null=True)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, verbose_name="Filial")
    demission = models.DateField("Demissão",null=True)
    situation = models.CharField("Sitaução Funcional",max_length=30)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.cod} - {self.name} - {self.cpf} - {self.ocupation} - {self.admission}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'colaboradores'
        verbose_name = 'colaborador'
    
class Events(models.Model):
    cod = models.IntegerField(unique=True)
    name = models.CharField(max_length=50)
    typeEvent = models.CharField(max_length=30)
    demonstrative = models.BooleanField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['cod']
        verbose_name_plural = 'eventos'
        verbose_name = 'evento'

class EventHistory(models.Model):
    cooperator = models.ForeignKey(Cooperators, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.CASCADE)
    movement = models.CharField(max_length=30,null=True)
    occurrence = models.DateField(null=True)
    competence = models.DateField()
    valuereference = models.FloatField()
    value = models.FloatField()
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.cooperator.cod}- {self.cooperator.name}- {self.competence} - {self.event.cod} - {self.event.name}"
    
    class Meta:
        ordering = ['competence','cooperator','event']
        verbose_name_plural = 'histórico de eventos'
        verbose_name = 'histórico de evento'

class GroupEvents(models.Model):
    name = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'grupos de eventos'
        verbose_name = 'grupo de eventos'

class EventsByGroup(models.Model):
    group = models.ForeignKey(GroupEvents, on_delete=models.CASCADE)
    event = models.ForeignKey(Events, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.id}"
    
    class Meta:
        ordering = ['group','event']
        verbose_name_plural = 'eventos por grupos'
        verbose_name = 'evento por grupo'
        
class Operador(models.Model):
    name = models.CharField(max_length=50)
    cod = models.CharField(max_length=12, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField("Ativo",default=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.cod} - {self.name}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'operadores'
        verbose_name = 'operador'
        
class Requisicao(models.Model):
    STATUS_CHOICE = (
        (1,'AGUARDANDO'),
        (2,'EM ATENDIMENTO'),
        (3,'FINALIZADA'),
    )
    CLASS_CHOICE = (
        (1,'INSUMO'),
        (2,'EPI'),
        (3,'OUTROS'),
    )
    PROGRESS_CHOICE = (
        (1,'NO PRAZO'),
        (2,'PENDENTE'),
        (3,'ATRASADO'),
        (4, 'CONCLUIDO'),
    )
    TIPO_CHOICE = (
        (1, 'EXTRA EVENTO'),
        (2, 'ERRO DE PLANEJAMENTO'),
        (3, 'ERRO DE ESTOQUE'),
        (4, 'AUMENTO DE COMENSAIS'),
        (5, 'AJUSTE DE CONTRATO'),
    )
    branch_solicitacao = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name="branch_solicitacao")
    branch_destino = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, related_name="branch_destino")
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, related_name="operador")
    dh_aprovacao = models.DateTimeField(null=True)
    nr_solicitacao = models.CharField(max_length=10)
    data_solicitacao = models.DateField()
    qtd_itens = models.IntegerField()
    justificativa = models.CharField(max_length=50)
    status = models.IntegerField('STATUS',choices=STATUS_CHOICE, default=1)
    classification = models.IntegerField('Classe', choices=CLASS_CHOICE, default=1)
    inicio_atendimento = models.BooleanField(default=False)
    operador_atendimento = models.ForeignKey(Operador, on_delete=models.SET_NULL, null=True, blank=True, related_name="operador_atendimento")
    dh_inicio_atendimento = models.DateTimeField(null=True, blank=True)
    finalizada = models.BooleanField(default=False)
    dh_finalizada = models.DateTimeField(null=True, blank=True)
    observation = models.TextField('Observações',blank=True)
    progress = models.IntegerField('Progresso',choices=PROGRESS_CHOICE, default=1)
    tipo = models.IntegerField('Tipo', choices=TIPO_CHOICE, default=1)
    valor = models.FloatField('Valor', default=0,blank=True)
    
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.nr_solicitacao} - {self.data_solicitacao} - {self.get_classification_display() } - {self.justificativa} - {self.get_status_display()}"
    
    class Meta:
        ordering = ['data_solicitacao','branch_solicitacao','nr_solicitacao']
        verbose_name_plural = 'requisições'
        verbose_name = 'requisição'

class ClassProduto(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=12, unique=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.name}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'classes de produtos'
        verbose_name = 'classe de produto'
 
class Produtos(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=12, unique=True)
    unidade = models.CharField(max_length=4)
    classification = models.ForeignKey(ClassProduto, on_delete=models.SET_NULL, null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.code} - {self.name} - {self.classification.name} - {self.unidade}"
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'produtos'
        verbose_name = 'produto'

class ItensRequisicao(models.Model):
    requisicao = models.ForeignKey(Requisicao, on_delete=models.CASCADE)
    produto = models.ForeignKey(Produtos, on_delete=models.SET_NULL, null=True)
    qtd = models.FloatField()
    dt_utiliza = models.DateField(null=True)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    def __str__(self):
        return f"{self.requisicao.nr_solicitacao} - {self.produto.name} - {self.qtd}"
    
    class Meta:
        ordering = ['requisicao','produto']
        verbose_name_plural = 'itens de requisições'
        verbose_name = 'item de requisição'