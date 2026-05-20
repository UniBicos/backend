from django.contrib import admin
from django.db.models import Sum

from .models import (
    Categorias,
    Compradores,
    EmailsInstituicao,
    Entregadores,
    InstituicoesEnsino,
    Lojas,
    Movimentacoes,
    Pagamento,
    PedidoProdutos,
    Pedidos,
    Produtos,
    SaquesLoja,
    Usuario,
)


class DadosCadForm(admin.ModelAdmin):
    readonly_fields = ["cad_por", "alt_por"]
    exclude = ["id_user_cad", "id_user_alt", "dt_alt"]

    def cad_por(self, instance):
        return (
            str(getattr(instance.id_user_cad, "nome", instance.id_user_cad.email))
            + " em "
            + instance.dt_cad.strftime("%d/%m/%Y")
        )

    def alt_por(self, instance):
        return (
            str(getattr(instance.id_user_alt, "nome", instance.id_user_alt.email))
            + " em "
            + instance.dt_alt.strftime("%d/%m/%Y")
        )

    cad_por.short_description = "Cadastrado por"
    alt_por.short_description = "Alterador por"

    def save_model(self, request, obj, form, change):
        if change and obj.id_user_cad is not None:
            obj.id_user_alt = request.user
        else:
            obj.id_user_cad = request.user
        obj.save()

    def save_formset(self, request, form, formset, change):
        for f in formset.forms:
            try:
                if f.instance.id_user_cad is not None:
                    f.instance.id_user_alt = request.user
            except:
                try:
                    f.instance.id_user_cad = request.user
                except:
                    print("o objeto nao possui dados cad")

        formset.save()


class PedidoProdutosInline(admin.TabularInline):
    model = PedidoProdutos
    extra = 1
    autocomplete_fields = ["id_produto"]


class InstituicoesEnsinoAdmin(DadosCadForm):
    list_display = ("sigla", "nome", "campus", "cidade", "estado")
    search_fields = ["nome", "sigla", "cidade"]
    readonly_fields = "id_user_cad", "id_user_alt"
    list_filter = ["estado"]

    fieldsets = (
        ("Dados Gerais", {"fields": ("nome", "sigla", "campus")}),
        ("Localização", {"fields": ("cidade", "estado")}),
        (
            "Outros",
            {"classes": ("collapse",), "fields": ("id_user_cad", "id_user_alt")},
        ),
    )


class EmailsInstituicaoAdmin(DadosCadForm):
    list_display = ("email", "id_instituicao")
    search_fields = ["email"]
    autocomplete_fields = ["id_instituicao"]


class UsuarioAdmin(DadosCadForm):
    list_display = ("nome", "cpf", "telefone", "id_instituicao")
    search_fields = ["nome", "cpf", "telefone"]
    autocomplete_fields = ["id_instituicao"]
    readonly_fields = "id_user_cad", "id_user_alt"

    fieldsets = (
        (
            "Dados Pessoais",
            {
                "fields": (
                    ("nome", "telefone"),
                    ("cpf", "cnpj"),
                    ("id_instituicao", "matricula"),
                )
            },
        ),
        (
            "Outros",
            {"classes": ("collapse",), "fields": ("id_user_cad", "id_user_alt")},
        ),
    )


class MovimentacoesAdmin(DadosCadForm):
    list_display = ("id_usuario", "tipo_perfil", "valor")
    list_filter = ("tipo_perfil",)
    search_fields = ["id_usuario__nome"]
    autocomplete_fields = ["id_usuario"]


class CompradoresAdmin(DadosCadForm):
    list_display = ("id_comprador", "id_usuario")
    search_fields = ["id_usuario__nome"]
    autocomplete_fields = ["id_usuario"]


class LojasAdmin(DadosCadForm):
    list_display = ("nome_fantasia", "id_usuario", "aberto", "avaliacao")
    list_filter = ("aberto",)
    search_fields = ["nome_fantasia", "id_usuario__nome"]
    autocomplete_fields = ["id_usuario"]


class SaquesLojaAdmin(DadosCadForm):
    list_display = ("id_saque", "id_loja", "valor", "status", "dt_cad")
    list_filter = ("status",)
    search_fields = ["id_loja__nome_fantasia", "pix"]
    autocomplete_fields = ["id_loja"]


class EntregadoresAdmin(DadosCadForm):
    list_display = ("id_usuario", "aberto", "saldo_disponivel", "avaliacao")
    list_filter = ("aberto",)
    search_fields = ["id_usuario__nome"]
    autocomplete_fields = ["id_usuario"]


class CategoriasAdmin(DadosCadForm):
    list_display = ("nome_categoria", "icon")
    search_fields = ["nome_categoria"]


class ProdutosAdmin(DadosCadForm):
    list_display = ("nome", "id_loja", "preco", "disponivel")
    list_filter = ("disponivel", "id_categoria")
    search_fields = ["nome"]
    autocomplete_fields = ["id_loja", "id_categoria"]

    fieldsets = (
        ("Produto", {"fields": ("nome", "descricao", "imagem")}),
        ("Relacionamentos", {"fields": ("id_loja", "id_categoria")}),
        ("Venda", {"fields": ("preco", "disponivel")}),
    )


class PedidosAdmin(DadosCadForm):
    list_display = (
        "id_pedido",
        "id_cliente",
        "id_loja",
        "status_pedido",
        "total_pedido",
    )
    list_filter = ("status_pedido",)
    search_fields = ["id_pedido"]
    autocomplete_fields = ["id_cliente", "id_loja", "id_entregador"]
    inlines = [PedidoProdutosInline]

    fieldsets = (
        ("Pedido", {"fields": ("id_cliente", "id_loja", "id_entregador")}),
        ("Valores", {"fields": ("taxa_entrega", "total_pedido")}),
        ("Entrega", {"fields": ("sala_entrega", "bloco_entrega", "descricao_local")}),
        ("Status", {"fields": ("status_pedido",)}),
    )

    def save_model(self, request, obj, form, change):
        if change:
            obj.id_user_alt = request.user
        else:
            obj.id_user_cad = request.user
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        total = (
            PedidoProdutos.objects.filter(id_pedido=form.instance).aggregate(
                total=Sum("preco_un")
            )["total"]
            or 0
        )

        form.instance.total_pedido = total
        form.instance.save()


class PedidoProdutosAdmin(DadosCadForm):
    list_display = ("id_pedido", "id_produto", "quantidade", "preco_un")
    search_fields = ["id_pedido__id_pedido", "id_produto__nome"]
    autocomplete_fields = ["id_pedido", "id_produto"]


class PagamentoAdmin(DadosCadForm):
    list_display = ("id_pagamento", "id_pedido", "status_pagamento")
    list_filter = ("status_pagamento",)
    autocomplete_fields = ["id_pedido"]


admin.site.register(InstituicoesEnsino, InstituicoesEnsinoAdmin)
admin.site.register(EmailsInstituicao, EmailsInstituicaoAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Movimentacoes, MovimentacoesAdmin)
admin.site.register(Compradores, CompradoresAdmin)
admin.site.register(Lojas, LojasAdmin)
admin.site.register(SaquesLoja, SaquesLojaAdmin)
admin.site.register(Entregadores, EntregadoresAdmin)
admin.site.register(Categorias, CategoriasAdmin)
admin.site.register(Produtos, ProdutosAdmin)
admin.site.register(Pedidos, PedidosAdmin)
admin.site.register(PedidoProdutos, PedidoProdutosAdmin)
admin.site.register(Pagamento, PagamentoAdmin)
