from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Produtos
from unibicos.serializers import ProdutosSerializer


class ProdutosViewSet(viewsets.ViewSet):
    queryset = Produtos.objects.all()
    serializer_class = ProdutosSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def list(self, request):
        queryset = Produtos.objects.all()

        id_loja = request.query_params.get('id_loja')
        if id_loja:
            queryset = queryset.filter(id_loja=id_loja)

        return Response(ProdutosSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            produto = Produtos.objects.get(id_produto=pk)
        except Produtos.DoesNotExist:
            return Response({'error': 'Produto não encontrado'}, status=404)

        return Response(ProdutosSerializer(produto).data)

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'nome_produto': {'type': 'string'},
                    'descricao': {'type': 'string'},
                    'preco': {'type': 'integer'},
                    'id_loja': {'type': 'integer'},
                    'id_categoria': {'type': 'integer'},
                    'disponivel': {'type': 'boolean'},
                    'imagem': {'type': 'string', 'format': 'binary'},
                },
                'required': ['nome_produto', 'imagem'],
            }
        }
    )
    def create(self, request):
        request.data['id_user_cad'] = request.user.id
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Produto cadastrado com sucesso.'}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            produto = Produtos.objects.get(id_produto=pk)
        except Produtos.DoesNotExist:
            return Response({'error': 'Produto não encontrado'}, status=404)

        request.data['id_user_alt'] = request.user.id
        serializer = self.serializer_class(produto, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Produto alterado com sucesso'})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            produto = Produtos.objects.get(id_produto=pk)
        except Produtos.DoesNotExist:
            return Response({'error': 'Produto não encontrado'}, status=404)

        produto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def mais_vendidos(self, request):
        queryset = Produtos.objects.all()

        id_loja = request.query_params.get('id_loja')
        if id_loja:
            queryset = queryset.filter(id_loja=id_loja)

        queryset = queryset.annotate(
            total_pedidos=Coalesce(Count('itens_pedido__id_pedido', distinct=True), Value(0))
        ).order_by('-total_pedidos')

        return Response(ProdutosSerializer(queryset, many=True).data)
