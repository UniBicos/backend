from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action

from unibicos.models import (
    Pedidos,
    PedidoProdutos,
    Produtos,
    Compradores,
    Pagamento,
)

from unibicos.serializers import (
    CarrinhoSerializer,
    AdicionarAoCarrinhoSerializer,
)


class CarrinhoViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @staticmethod
    def atualizar_total(pedido):
        itens = PedidoProdutos.objects.filter(id_pedido=pedido)

        total = sum(item.quantidade * item.preco_un for item in itens)

        pedido.total_pedido = total
        pedido.save()

    def list(self, request):
        """Pega o carrinho atual (pedido com status RASCUNHO)"""
        print(request.user.id)
        comprador = Compradores.objects.get(id_usuario=request.user.id)

        if not comprador:
            return Response(
                {"error": "Nenhum comprador encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        pedido = Pedidos.objects.filter(
            id_cliente=comprador.id_comprador,
            status_pedido="RASCUNHO",
        ).first()

        if not pedido:
            return Response(
                {
                    "id_pedido": None,
                    "status_pedido": "RASCUNHO",
                    "total_pedido": 0,
                    "taxa_entrega": 0,
                    "itens": [],
                    "total": 0,
                }
            )

        serializer = CarrinhoSerializer(pedido)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="adicionar",
    )
    def adicionar_ao_carrinho(self, request):
        """Adiciona produto ao carrinho"""
        serializer = AdicionarAoCarrinhoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        id_produto = serializer.validated_data["id_produto"]
        quantidade = serializer.validated_data["quantidade"]

        produto = Produtos.objects.get(id_produto=id_produto)
        comprador = Compradores.objects.get(id_usuario=request.user.id)

        if not comprador:
            return Response(
                {"error": "Nenhum comprador encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        pedido, created = Pedidos.objects.get_or_create(
            id_cliente=comprador,
            id_loja=produto.id_loja,
            status_pedido="RASCUNHO",
            defaults={
                "total_pedido": 0,
                "taxa_entrega": 0,
            },
        )

        item, item_created = PedidoProdutos.objects.get_or_create(
            id_pedido=pedido,
            id_produto=produto,
            defaults={
                "quantidade": quantidade,
                "preco_un": produto.preco,
            },
        )

        if not item_created:
            item.quantidade = quantidade
            item.save()

        if quantidade <= 0:
            item.delete()

        self.atualizar_total(pedido)

        carrinho_serializer = CarrinhoSerializer(pedido)
        return Response(carrinho_serializer.data)

    @action(
        detail=False,
        methods=["delete"],
        url_path="remover/(?P<id_produto>[^/.]+)",
    )
    def remover_produto(self, request, id_produto=None):
        """Remove produto do carrinho"""
        comprador = Compradores.objects.get(id_usuario=request.user.id)

        if not comprador:
            return Response(
                {"error": "Nenhum comprador encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        pedido = Pedidos.objects.filter(
            id_cliente=comprador.id_comprador,
            status_pedido="RASCUNHO",
        ).first()

        if not pedido:
            return Response(
                {"error": "Carrinho não encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        PedidoProdutos.objects.filter(
            id_pedido=pedido.id_pedido,
            id_produto=id_produto,
        ).delete()

        self.atualizar_total(pedido)

        carrinho_serializer = CarrinhoSerializer(pedido)
        return Response(carrinho_serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="finalizar",
    )
    def finalizar(self, request):
        """Finaliza o carrinho (checkout)"""
        comprador = Compradores.objects.get(id_usuario=request.user.id)

        if not comprador:
            return Response(
                {"error": "Nenhum comprador encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )

        pedido = Pedidos.objects.filter(
            id_cliente=comprador.id_comprador,
            status_pedido="RASCUNHO",
        ).first()

        if not pedido:
            return Response(
                {"error": "Carrinho vazio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        itens = PedidoProdutos.objects.filter(id_pedido=pedido)

        if not itens.exists():
            return Response(
                {"error": "Carrinho vazio"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pedido.status_pedido = "CRIADO"
        pedido.save()

        Pagamento.objects.create(
            id_pedido=pedido,
            status_pagamento="AGUARDANDO_PAGAMENTO",
        )

        carrinho_serializer = CarrinhoSerializer(pedido)
        return Response(carrinho_serializer.data)
