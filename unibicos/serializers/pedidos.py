from rest_framework import serializers

from .produtos import ProdutosSerializer
from unibicos.models import PedidoProdutos, Pedidos, Produtos


class PedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedidos
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id": obj.id_pedido,
            "id_cliente": obj.id_cliente.id_usuario,
            "id_loja": obj.id_loja.id_loja,
            "id_entregador": (obj.id_entregador.id_usuario if obj.id_entregador else None),
            "status": obj.status_pedido,
            "total": obj.total,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }


class PedidoProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoProdutos
        fields = "__all__"

    def to_representation(self, obj):

        return {
            "id_pedido_produto": obj.id_pedido_produto,
            "id_pedido": PedidosSerializer(Pedidos.objects.get(pk=obj.id_pedido.pk)),
            "id_produto": ProdutosSerializer(Produtos.objects.get(pk=obj.id_produto.pk)),
            "quantidade": obj.quantidade,
            "preco_un": obj.preco_un,
        }
