from rest_framework import serializers

from .produtos import ProdutosSerializer
from unibicos.models import PedidoProdutos, Pedidos, Produtos


class PedidosSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="status_pedido", required=False)

    class Meta:
        model = Pedidos
        exclude = ["status_pedido"]

    def to_representation(self, obj):
        return {
            "id": obj.id_pedido,
            "id_cliente": obj.id_cliente.id_usuario.id,
            "id_loja": obj.id_loja.id_loja,
            "id_entregador": (obj.id_entregador.id_usuario.id if obj.id_entregador else None),
            "status": obj.status_pedido,
            "total": obj.total_pedido,
            "created_at": obj.dt_cad,
            "updated_at": obj.dt_alt,
        }


class PedidoProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoProdutos
        fields = "__all__"

    def to_representation(self, obj):

        return {
            "id_pedido_produto": obj.id_pedido_produto,
            "id_pedido": PedidosSerializer(Pedidos.objects.get(pk=obj.id_pedido.pk)).data,
            "id_produto": ProdutosSerializer(Produtos.objects.get(pk=obj.id_produto.pk)).data,
            "quantidade": obj.quantidade,
            "preco_un": obj.preco_un,
        }
