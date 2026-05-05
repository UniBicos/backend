from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Compradores
from unibicos.serializers import CompradoresSerializer


class CompradoresViewSet(viewsets.ViewSet):
    queryset = Compradores.objects.all()
    serializer_class = CompradoresSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Compradores.objects.all()
        return Response(CompradoresSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            comprador = Compradores.objects.get(id_comprador=pk)
        except Compradores.DoesNotExist:
            return Response({"error": "Comprador não encontrado"}, status=404)

        return Response(CompradoresSerializer(comprador).data)

    def create(self, request):
        request.data["id_user_cad"] = request.user.id
        serializer = CompradoresSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Comprador cadastrado com sucesso"}, status=201)
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            comprador = Compradores.objects.get(id_comprador=pk)
        except Compradores.DoesNotExist:
            return Response({"error": "Comprador não encontrado"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = CompradoresSerializer(comprador, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Comprador alterado com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            comprador = Compradores.objects.get(id_comprador=pk)
        except Compradores.DoesNotExist:
            return Response({"error": "Comprador não encontrado"}, status=404)

        comprador.delete()
        return Response(status=204)
