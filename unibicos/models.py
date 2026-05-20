import re

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from core import settings
from core import settings
from unibicos.managers import UsuarioManager

status_pedido_choices = [
    ("RASCUNHO", "RASCUNHO"),
    ("CRIADO", "CRIADO"),
    ("ACEITO_PELO_VENDEDOR", "ACEITO_PELO_VENDEDOR"),
    ("EM_PREPARO", "EM_PREPARO"),
    ("ENTREGA_ACEITA", "ENTREGA_ACEITA"),
    ("SAIU_PARA_ENTREGA", "SAIU_PARA_ENTREGA"),
    ("ENTREGUE", "ENTREGUE"),
    ("CANCELADO", "CANCELADO"),
]

tipos_perfil_choices = [
    ("ENTREGADOR", "ENTREGADOR"),
    ("LOJA", "LOJA"),
]

status_pagamento_choices = [
    ("AGUARDANDO_PAGAMENTO", "AGUARDANDO_PAGAMENTO"),
    ("PAGO", "PAGO"),
    ("CONFIRMADO", "CONFIRMADO"),
    ("CANCELADO", "CANCELADO"),
]


def valida_cpf(value):
    if not re.match(r"^\d{11}$", value):
        raise ValidationError("O CPF deve conter exatamente 11 dígitos e somente números.")


def valida_cnpj(value):
    if not re.match(r"^\d{14}$", value):
        raise ValidationError("O CNPJ deve conter exatamente 14 dígitos e somente números.")


class BaseModel(models.Model):
    id_user_cad = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_user_cad",
    )
    dt_cad = models.DateTimeField(auto_now_add=True)

    id_user_alt = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_user_alt",
    )

    dt_alt = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Usuario(AbstractUser, BaseModel):
    username = None
    first_name = None
    last_name = None

    email = models.EmailField("Endereço de E-mail", max_length=200, unique=True)
    nome = models.CharField("Nome Completo", max_length=255)

    id_instituicao = models.ForeignKey(
        "InstituicoesEnsino", on_delete=models.SET_NULL, null=True, blank=True
    )
    cpf = models.CharField(
        max_length=11, validators=[valida_cpf], null=True, blank=True, unique=True
    )
    cnpj = models.CharField(
        max_length=14, validators=[valida_cnpj], null=True, blank=True, unique=True
    )
    telefone = models.CharField(max_length=15)
    matricula = models.CharField(max_length=50, null=True, blank=True)

    objects = UsuarioManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    class Meta:
        db_table = "tb_usuario"
        verbose_name_plural = "Usuarios"

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if self.cpf == "":
            self.cpf = None
        if self.cnpj == "":
            self.cnpj = None

        super().save(*args, **kwargs)


class InstituicoesEnsino(BaseModel):
    id_instituicao = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=80)
    sigla = models.CharField(max_length=10)
    campus = models.CharField(max_length=50)
    cidade = models.CharField(max_length=40)
    estado = models.CharField(max_length=40)

    class Meta:
        db_table = "tb_instituicoes_ensino"
        ordering = ["nome"]
        verbose_name_plural = "Instituições de Ensino"

    def __str__(self):
        return self.sigla + " - " + self.nome


class EmailsInstituicao(BaseModel):
    id_email_instituicao = models.AutoField(primary_key=True)
    id_instituicao = models.ForeignKey(
        InstituicoesEnsino, on_delete=models.CASCADE, related_name="emails_instituicao"
    )
    email = models.EmailField(max_length=200)

    class Meta:
        db_table = "tb_emails_ensino"
        ordering = ["email"]
        verbose_name_plural = "Emails da Instituição"

    def __str__(self):
        return self.email


class Movimentacoes(BaseModel):
    id_movimentacoes = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    tipo_perfil = models.CharField(max_length=20, default="LOJA", choices=tipos_perfil_choices)
    valor = models.IntegerField(default=0)

    class Meta:
        db_table = "tb_movimentacoes"
        ordering = ["id_movimentacoes"]
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return str(self.id_usuario) + " - " + self.tipo_perfil


class Compradores(BaseModel):
    id_comprador = models.AutoField(primary_key=True)
    id_usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name="comprador")

    class Meta:
        db_table = "tb_compradores"
        ordering = ["id_comprador"]
        verbose_name_plural = "Compradores"

    def __str__(self):
        return str(self.id_comprador)


class Lojas(BaseModel):
    id_loja = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="lojas")
    nome_fantasia = models.CharField(max_length=120)
    aberto = models.BooleanField(default=False)
    departamento = models.CharField(max_length=120, null=True, blank=True)
    localizacao = models.CharField(max_length=300)
    avaliacao = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=5.0,
    )
    saldo_disponivel = models.IntegerField(default=0)
    imagem = models.ImageField(upload_to="produtos/", null=True, blank=True)

    class Meta:
        db_table = "tb_lojas"
        ordering = ["nome_fantasia"]
        verbose_name_plural = "Lojas"

    def __str__(self):
        return self.nome_fantasia


class Entregadores(BaseModel):
    id_entregador = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name="entregadores")
    aberto = models.BooleanField(default=False)
    saldo_disponivel = models.IntegerField(default=0)
    avaliacao = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        default=5.0,
    )

    class Meta:
        db_table = "tb_entregadores"
        ordering = ["id_entregador"]
        verbose_name_plural = "Entregadores"

    def __str__(self):
        return str(self.id_usuario)


class Categorias(BaseModel):
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=200)
    icon = models.CharField(max_length=200)

    class Meta:
        db_table = "tb_categorias"
        ordering = ["nome_categoria"]
        verbose_name_plural = "Categorias"

    def __str__(self):
        return self.nome_categoria


class Produtos(BaseModel):
    id_produto = models.AutoField(primary_key=True)
    id_loja = models.ForeignKey(Lojas, on_delete=models.CASCADE, related_name="produtos")
    id_categoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    imagem = models.ImageField(upload_to="produtos/", null=True, blank=True)
    descricao = models.CharField(max_length=600)
    preco = models.FloatField(default=0)
    disponivel = models.BooleanField(default=False)

    class Meta:
        db_table = "tb_produtos"
        ordering = ["nome"]
        verbose_name_plural = "Produtos"

    def __str__(self):
        return self.nome


class Pedidos(BaseModel):
    id_pedido = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Compradores, on_delete=models.CASCADE)
    id_loja = models.ForeignKey(Lojas, on_delete=models.CASCADE)
    id_entregador = models.ForeignKey(
        Entregadores, on_delete=models.CASCADE, null=True, blank=True
    )
    taxa_entrega = models.FloatField(default=0)
    total_pedido = models.FloatField(default=0)
    status_pedido = models.CharField(
        max_length=20, default="CRIADO", choices=status_pedido_choices
    )
    token = models.CharField(max_length=4)
    sala_entrega = models.CharField(max_length=50, null=True, blank=True)
    bloco_entrega = models.CharField(max_length=100, null=True, blank=True)
    descricao_local = models.CharField(max_length=600, null=True, blank=True)

    class Meta:
        db_table = "tb_pedidos"
        ordering = ["id_pedido"]
        verbose_name_plural = "Pedidos"

    def __str__(self):
        return str(self.id_pedido) + " - R$ " + str(self.total_pedido)

    def save(self, *args, **kwargs):
        if not self.token:
            telefone = self.id_cliente.id_usuario.telefone
            self.token = telefone[-4:]
        super().save(*args, **kwargs)


class PedidoProdutos(BaseModel):
    id_pedido_produto = models.AutoField(primary_key=True)
    id_pedido = models.ForeignKey(Pedidos, on_delete=models.CASCADE)
    id_produto = models.ForeignKey(Produtos, on_delete=models.CASCADE, related_name="itens_pedido")
    quantidade = models.IntegerField(default=1)
    preco_un = models.FloatField(default=0)

    class Meta:
        db_table = "tb_pedido_produtos"
        unique_together = ("id_pedido", "id_produto")
        ordering = ["id_pedido_produto"]
        verbose_name_plural = "Produtos de pedido"

    def __str__(self):
        return str(self.id_pedido) + str(self.id_produto)


class Pagamento(BaseModel):
    id_pagamento = models.AutoField(primary_key=True)
    id_pedido = models.OneToOneField(Pedidos, on_delete=models.CASCADE)
    id_intent = models.CharField(max_length=200, unique=True, null=True, blank=True)
    status_pagamento = models.CharField(
        max_length=20, default="AGUARDANDO_PAGAMENTO", choices=status_pagamento_choices
    )

    class Meta:
        db_table = "tb_pagamentos"
        ordering = ["id_pagamento"]
        verbose_name_plural = "Pagamentos"

    def __str__(self):
        return str(self.id_pagamento) + " - " + self.status_pagamento
