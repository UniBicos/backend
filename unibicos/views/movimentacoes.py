from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Movimentacoes
from unibicos.serializers import MovimentacoesSerializer


class MovimentacoesViewSet(viewsets.ViewSet):
    queryset = Movimentacoes.objects.all()
    serializer_class = MovimentacoesSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Movimentacoes.objects.all()
        return Response(MovimentacoesSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            movimentacao = Movimentacoes.objects.get(id_movimentacoes=pk)
        except Movimentacoes.DoesNotExist:
            return Response({"error": "Movimentação não encontrada"}, status=404)

        return Response(MovimentacoesSerializer(movimentacao).data)

    def create(self, request):
        request.data["id_user_cad"] = request.user.id
        serializer = MovimentacoesSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Movimentação cadastrada com sucesso"}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            movimentacao = Movimentacoes.objects.get(id_movimentacoes=pk)
        except Movimentacoes.DoesNotExist:
            return Response({"error": "Movimentação não encontrada"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = MovimentacoesSerializer(movimentacao, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Movimentação alterada com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            movimentacao = Movimentacoes.objects.get(id_movimentacoes=pk)
        except Movimentacoes.DoesNotExist:
            return Response({"error": "Movimentação não encontrada"}, status=404)

        movimentacao.delete()
        return Response(status=204)
