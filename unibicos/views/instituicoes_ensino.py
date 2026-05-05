from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import InstituicoesEnsino
from unibicos.serializers import InstituicoesEnsinoSerializer


class InstituicoesEnsinoViewSet(viewsets.ViewSet):
    queryset = InstituicoesEnsino.objects.all()
    serializer_class = InstituicoesEnsinoSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = InstituicoesEnsino.objects.all()
        return Response(InstituicoesEnsinoSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            instituicao_ensino = InstituicoesEnsino.objects.get(id_instituicao=pk)
        except InstituicoesEnsino.DoesNotExist:
            return Response({"error": "Instituição de Ensino não encontrado"}, status=404)

        return Response(InstituicoesEnsinoSerializer(instituicao_ensino).data)

    def create(self, request):
        request.data["id_user_cad"] = request.user.id
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Instituição de Ensino cadastrado com sucesso"}, status=201
            )
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        try:
            instituicao_ensino = InstituicoesEnsino.objects.get(id_instituicao=pk)
        except InstituicoesEnsino.DoesNotExist:
            return Response({"error": "Instituição de Ensino não encontrado"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = self.serializer_class(instituicao_ensino, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Instituição de Ensino alterado com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            instituicao_ensino = InstituicoesEnsino.objects.get(id_instituicao=pk)
        except InstituicoesEnsino.DoesNotExist:
            return Response({"error": "Instituição de Ensino não encontrado"}, status=404)

        instituicao_ensino.delete()
        return Response({"message": "Instituição de Ensino deletado com sucesso"}, status=204)
