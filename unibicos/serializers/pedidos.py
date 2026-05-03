from rest_framework import serializers

from unibicos.models import PedidoProdutos, Pedidos, Produtos


class PedidosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedidos
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id': obj.id_pedido,
            'clientId': obj.id_cliente.id_comprador,
            'sellerId': obj.id_loja.id_loja,
            'courierId': obj.id_entregador.id_entregador if obj.id_entregador else None,
            'totalPrice': obj.total_pedido,
            'deliveryFee': obj.taxa_entrega,
            'status': obj.status_pedido,
            'paymentMethod': 'PIX',  # Ajustar
            'deliveryLocation': {
                'latitude': 0,  # Ajustar
                'longitude': 0,
                'description': obj.descricao_local or '',
            },
            'verificationToken': obj.token,
            'createdAt': obj.dt_cad.isoformat() if obj.dt_cad else None,
            'completedAt': None,  # Ajustar
        }


class PedidoProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = PedidoProdutos
        fields = '__all__'

    def to_representation(self, obj):
        from .produtos import ProdutosSerializer

        return {
            'id_pedido_produto': obj.id_pedido_produto,
            'id_pedido': PedidosSerializer(Pedidos.objects.get(pk=obj.id_pedido.pk)),
            'id_produto': ProdutosSerializer(Produtos.objects.get(pk=obj.id_produto.pk)),
            'quantidade': obj.quantidade,
            'preco_un': obj.preco_un,
        }
