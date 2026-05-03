from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from unibicos.models import Lojas, Produtos
from unibicos.serializers import LojasSerializer, ProdutosSerializer


class LojasViewSet(viewsets.ViewSet):
    queryset = Lojas.objects.all()
    serializer_class = LojasSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = Lojas.objects.all()
        return Response(LojasSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            loja = Lojas.objects.get(id_loja=pk)
        except Lojas.DoesNotExist:
            return Response({'error': 'Loja não encontrada'}, status=404)

        produtos = Produtos.objects.filter(id_loja=loja.id_loja)
        data = LojasSerializer(loja).data
        data['products'] = ProdutosSerializer(produtos, many=True).data
        return Response(data)

    def create(self, request):
        request.data['id_user_cad'] = request.user.id
        serializer = LojasSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Loja cadastrada com sucesso'}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            loja = Lojas.objects.get(id_loja=pk)
        except Lojas.DoesNotExist:
            return Response({'error': 'Loja não encontrada'}, status=404)

        request.data['id_user_alt'] = request.user.id
        serializer = LojasSerializer(loja, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Loja alterada com sucesso'})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            loja = Lojas.objects.get(id_loja=pk)
        except Lojas.DoesNotExist:
            return Response({'error': 'Loja não encontrada'}, status=404)

        loja.delete()
        return Response({'message': 'Loja deletada com sucesso'}, status=204)
