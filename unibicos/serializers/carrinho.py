# unibicos/serializers.py
from rest_framework import serializers
from ..models import Pedidos, PedidoProdutos, Produtos


class ProdutoCarrinhoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = ["id_produto", "nome", "preco", "imagem", "descricao"]


class ItemCarrinhoSerializer(serializers.ModelSerializer):
    produto = ProdutoCarrinhoSerializer(source="id_produto", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = PedidoProdutos
        fields = ["id_produto", "produto", "quantidade", "preco_un", "subtotal"]

    def get_subtotal(self, obj):
        return obj.quantidade * obj.preco_un


class CarrinhoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="id_pedido", read_only=True)

    itens = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    loja_nome = serializers.CharField(source="id_loja.nome_fantasia", read_only=True)

    class Meta:
        model = Pedidos
        fields = [
            "id",
            "status_pedido",
            "total_pedido",
            "taxa_entrega",
            "loja_nome",
            "itens",
            "total",
        ]

    def get_itens(self, obj):
        itens = PedidoProdutos.objects.filter(id_pedido=obj)
        return ItemCarrinhoSerializer(itens, many=True).data

    def get_total(self, obj):
        itens = PedidoProdutos.objects.filter(id_pedido=obj)
        total = sum(item.quantidade * item.preco_un for item in itens)
        return total + (obj.taxa_entrega or 0)


class AdicionarAoCarrinhoSerializer(serializers.Serializer):
    id_produto = serializers.IntegerField()
    quantidade = serializers.IntegerField(min_value=1)
