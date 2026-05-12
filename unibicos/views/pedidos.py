from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Pedidos, PedidoProdutos, Produtos, Lojas
from unibicos.serializers import PedidosSerializer, PedidoProdutosSerializer


class PedidosViewSet(viewsets.ViewSet):
    queryset = Pedidos.objects.all()
    serializer_class = PedidosSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Pedidos.objects.all()

        id_cliente = request.query_params.get("id_cliente")
        id_loja = request.query_params.get("id_loja")
        id_entregador = request.query_params.get("id_entregador")
        status_pedido = self.request.query_params.get("status")

        if id_cliente:
            queryset = queryset.filter(id_cliente=id_cliente)
        if id_loja:
            queryset = queryset.filter(id_loja=id_loja)
        if id_entregador:
            queryset = queryset.filter(id_entregador=id_entregador)
        if status_pedido:
            queryset = queryset.filter(status_pedido=status_pedido)

        data = PedidosSerializer(queryset, many=True).data
        pedido_produtos = PedidoProdutos.objects.filter(id_pedido=item["id"])
        item["produtos"] = pedido_produtos
        if not id_loja:
            for item in data:
                loja = Lojas.objects.get(id_loja=item["loja_id"])
                item["loja"] = loja

        return Response(data)

    def retrieve(self, request, pk=None):
        try:
            pedido = Pedidos.objects.get(id_pedido=pk)
        except Pedidos.DoesNotExist:
            return Response({"error": "Pedido não encontrado"}, status=404)

        return Response(PedidosSerializer(pedido).data)

    def create(self, request):
        request.data["id_user_cad"] = request.user.id
        serializer = PedidosSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Pedido cadastrado com sucesso"}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            pedido = Pedidos.objects.get(id_pedido=pk)
        except Pedidos.DoesNotExist:
            return Response({"error": "Pedido não encontrado"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = PedidosSerializer(pedido, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Pedido alterado com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            pedido = Pedidos.objects.get(id_pedido=pk)
        except Pedidos.DoesNotExist:
            return Response({"error": "Pedido não encontrado"}, status=404)

        pedido.delete()
        return Response({"message": "Pedido deletado com sucesso"}, status=204)
