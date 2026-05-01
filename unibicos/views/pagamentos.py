from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Pagamento
from unibicos.serializers import PagamentoSerializer


class PagamentoViewSet(viewsets.ViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Pagamento.objects.all()
        return Response(PagamentoSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            pagamento = Pagamento.objects.get(id_pagamento=pk)
        except Pagamento.DoesNotExist:
            return Response({'error': 'Pagamento não encontrado'}, status=404)

        return Response(PagamentoSerializer(pagamento).data)

    def create(self, request):
        request.data['id_user_cad'] = request.user.id
        serializer = PagamentoSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Pagamento cadastrado com sucesso'}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            pagamento = Pagamento.objects.get(id_pagamento=pk)
        except Pagamento.DoesNotExist:
            return Response({'error': 'Pagamento não encontrado'}, status=404)

        request.data['id_user_alt'] = request.user.id
        serializer = PagamentoSerializer(pagamento, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Pagamento alterado com sucesso'})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            pagamento = Pagamento.objects.get(id_pagamento=pk)
        except Pagamento.DoesNotExist:
            return Response({'error': 'Pagamento não encontrado'}, status=404)

        pagamento.delete()
        return Response(status=204)
