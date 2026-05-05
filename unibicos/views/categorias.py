from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from unibicos.models import Categorias
from unibicos.serializers import CategoriasSerializer


class CategoriasViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    queryset = Categorias.objects.all()
    serializer_class = CategoriasSerializer

    def list(self, request):
        queryset = Categorias.objects.all()
        return Response(CategoriasSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            categoria = Categorias.objects.get(id_categoria=pk)
        except Categorias.DoesNotExist:
            return Response({"error": "Categoria não encontrada"}, status=404)

        return Response(CategoriasSerializer(categoria).data)
