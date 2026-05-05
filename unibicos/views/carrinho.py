# unibicos/views/carrinho.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Pedidos, PedidoProdutos, Produtos, Compradores
from ..serializers import CarrinhoSerializer, AdicionarAoCarrinhoSerializer  # Importa do __init__.py

@api_view(['GET'])
@permission_classes([AllowAny])
def get_carrinho(request):
    """Pega o carrinho atual (pedido com status RASCUNHO)"""
    comprador = Compradores.objects.first()
    
    if not comprador:
        return Response({'error': 'Nenhum comprador encontrado'}, status=404)
    
    pedido = Pedidos.objects.filter(
        id_cliente=comprador,
        status_pedido='RASCUNHO'
    ).first()
    
    if not pedido:
        return Response({
            'id_pedido': None,
            'status_pedido': 'RASCUNHO',
            'total_pedido': 0,
            'taxa_entrega': 0,
            'itens': [],
            'total': 0
        })
    
    serializer = CarrinhoSerializer(pedido)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def adicionar_ao_carrinho(request):
    """Adiciona produto ao carrinho"""
    serializer = AdicionarAoCarrinhoSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    
    produto_id = serializer.validated_data['id_produto']
    quantidade = serializer.validated_data['quantidade']
    
    produto = get_object_or_404(Produtos, id_produto=produto_id)
    comprador = Compradores.objects.first()
    
    if not comprador:
        return Response({'error': 'Nenhum comprador encontrado'}, status=404)
    
    pedido, created = Pedidos.objects.get_or_create(
        id_cliente=comprador,
        id_loja=produto.id_loja,
        status_pedido='RASCUNHO',
        defaults={'total_pedido': 0, 'taxa_entrega': 0}
    )
    
    item, item_created = PedidoProdutos.objects.get_or_create(
        id_pedido=pedido,
        id_produto=produto,
        defaults={'quantidade': quantidade, 'preco_un': produto.preco}
    )
    
    if not item_created:
        item.quantidade = quantidade
        item.save()
    
    if quantidade <= 0:
        item.delete()
    
    # Atualiza total
    itens = PedidoProdutos.objects.filter(id_pedido=pedido)
    total = sum(item.quantidade * item.preco_un for item in itens)
    pedido.total_pedido = total
    pedido.save()
    
    carrinho_serializer = CarrinhoSerializer(pedido)
    return Response(carrinho_serializer.data)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def remover_do_carrinho(request, produto_id):
    """Remove um produto do carrinho"""
    comprador = Compradores.objects.first()
    
    if not comprador:
        return Response({'error': 'Nenhum comprador encontrado'}, status=404)
    
    pedido = Pedidos.objects.filter(
        id_cliente=comprador,
        status_pedido='RASCUNHO'
    ).first()
    
    if not pedido:
        return Response({'error': 'Carrinho não encontrado'}, status=404)
    
    PedidoProdutos.objects.filter(
        id_pedido=pedido,
        id_produto_id=produto_id
    ).delete()
    
    itens = PedidoProdutos.objects.filter(id_pedido=pedido)
    total = sum(item.quantidade * item.preco_un for item in itens)
    pedido.total_pedido = total
    pedido.save()
    
    carrinho_serializer = CarrinhoSerializer(pedido)
    return Response(carrinho_serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def finalizar_carrinho(request):
    """Finaliza o carrinho (checkout)"""
    comprador = Compradores.objects.first()
    
    if not comprador:
        return Response({'error': 'Nenhum comprador encontrado'}, status=404)
    
    pedido = Pedidos.objects.filter(
        id_cliente=comprador,
        status_pedido='RASCUNHO'
    ).first()
    
    if not pedido:
        return Response({'error': 'Carrinho vazio'}, status=400)
    
    itens = PedidoProdutos.objects.filter(id_pedido=pedido)
    if not itens.exists():
        return Response({'error': 'Carrinho vazio'}, status=400)
    
    pedido.status_pedido = 'CRIADO'
    pedido.save()
    
    from ..models import Pagamento
    Pagamento.objects.create(
        id_pedido=pedido,
        status_pagamento='AGUARDANDO_PAGAMENTO'
    )
    
    carrinho_serializer = CarrinhoSerializer(pedido)
    return Response(carrinho_serializer.data)