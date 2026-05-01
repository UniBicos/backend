from rest_framework import serializers

from unibicos.models import PedidoProdutos, Pedidos, Produtos
from unibicos.serializers.produtos import ProdutosSerializer


class PedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedidos
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id_pedido': obj.id_pedido,
            'id_cliente': obj.id_cliente.id_comprador,
            'id_loja': obj.id_loja.id_loja,
            'id_entregador': obj.id_entregador.id_entregador if obj.id_entregador else None,
            'taxa_entrega': obj.taxa_entrega,
            'total_pedido': obj.total_pedido,
            'status_pedido': obj.status_pedido,
            'token': obj.token,
            'sala_entrega': obj.sala_entrega,
            'bloco_entrega': obj.bloco_entrega,
            'descricao_local': obj.descricao_local,
        }


class PedidoProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoProdutos
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id_pedido_produto': obj.id_pedido_produto,
            'id_pedido': PedidosSerializer(Pedidos.objects.get(pk=obj.id_pedido.pk)),
            'id_produto': ProdutosSerializer(Produtos.objects.get(pk=obj.id_produto.pk)),
            'quantidade': obj.quantidade,
            'preco_un': obj.preco_un,
        }
