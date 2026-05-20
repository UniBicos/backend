from django.db.models import Count, Value
from django.db.models.functions import Coalesce
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from unibicos.models import Produtos, Lojas
from unibicos.serializers import ProdutosSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from unibicos.models import Lojas, Produtos
from unibicos.serializers import ProdutosSerializer, ProdutosInfoSerializer


class ProdutosViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ProdutosSerializer
    queryset = Produtos.objects.all()

    parser_classes = (MultiPartParser, FormParser)

    # =========================
    # LISTA SIMPLES DE PRODUTOS
    # =========================
    def list(self, request):
        queryset = Produtos.objects.all()

        id_loja = request.query_params.get("id_loja")
        query = request.query_params.get("query")
        category = request.query_params.get("category")

        if id_loja:
            queryset = queryset.filter(id_loja=id_loja)
        if query:
            queryset = queryset.filter(nome__icontains=query)
        if category:
            queryset = queryset.filter(id_categoria=category)

        serializer = ProdutosSerializer(queryset, many=True)
        data = serializer.data

        for item in data:
            loja = Lojas.objects.get(id_loja=item["id_loja"])
            item["loja"] = {
                "id": loja.id_loja,
                "id_usuario": loja.id_usuario.id,
                "nome_fantasia": loja.nome_fantasia,
                "imagem": "",  # Ajustar
            }
        return Response(data)

    # =========================
    # PRODUTO POR ID
    # =========================
    def retrieve(self, request, pk=None):
        try:
            produto = Produtos.objects.get(id_produto=pk)
        except Produtos.DoesNotExist:
            return Response({"error": "Produto não encontrado"}, status=404)

        serializer = ProdutosSerializer(produto)
        data = serializer.data
        return Response(data)

    # =========================
    # CRIAR PRODUTO
    # =========================
    def create(self, request):
        data = request.data.copy()
        data["id_user_cad"] = request.user.id

        serializer = ProdutosSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Produto cadastrado com sucesso."}, status=201)

        return Response(serializer.errors, status=400)

    # =========================
    # ATUALIZAR PRODUTO
    # =========================
    def partial_update(self, request, pk=None):
        try:
            produto = Produtos.objects.get(id_produto=pk)
        except Produtos.DoesNotExist:
            return Response({"error": "Produto não encontrado"}, status=404)

        data = request.data.copy()
        data["id_user_alt"] = request.user.id

        serializer = ProdutosSerializer(produto, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Produto alterado com sucesso"})

        return Response(serializer.errors, status=400)

    # =========================
    # DELETAR PRODUTO
    # =========================
    def destroy(self, request, pk=None):
        try:
            produto = Produtos.objects.get(id_produto=pk)
        except Produtos.DoesNotExist:
            return Response({"error": "Produto não encontrado"}, status=404)

        produto.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # =========================
    # MAIS VENDIDOS
    # =========================
    @action(detail=False, methods=["get"])
    def mais_vendidos(self, request):
        queryset = Produtos.objects.all()

        id_loja = request.query_params.get("id_loja")
        if id_loja:
            queryset = queryset.filter(id_loja=id_loja)

        queryset = queryset.annotate(
            total_pedidos=Coalesce(Count("itens_pedido__id_pedido", distinct=True), Value(0))
        ).order_by("-total_pedidos")

        return Response(ProdutosSerializer(queryset, many=True).data)

    @action(detail=False, methods=["get"])
    def stores_with_products(self, request):
        lojas = Lojas.objects.filter(aberto=True)

        resultado = []

        for loja in lojas:
            produtos = Produtos.objects.filter(id_loja=loja.id_loja, disponivel=True)
            institution_name = (
                loja.id_usuario.id_instituicao.sigla
                if loja.id_usuario and loja.id_usuario.id_instituicao
                else ""
            )

            resultado.append(
                {
                    "id_loja": loja.id_loja,
                    "id_usuario": loja.id_usuario.id,
                    "nome_fantasia": loja.nome_fantasia,
                    "informal": False,
                    "localizacao": loja.localizacao or "",
                    "imagem": "",
                    "avaliacao": loja.avaliacao,
                    "instituicao": institution_name,
                    "departamento": loja.departamento,
                    "aberto": loja.aberto,
                    "saldo_disponivel": loja.saldo_disponivel,
                    "produtos": ProdutosInfoSerializer(produtos, many=True).data,
                }
            )

        return Response(resultado)

    @action(detail=False, methods=["get"])
    def categorized_products(self, request):
        category_id = request.query_params.get("category")
        queryset = Produtos.objects.select_related("id_categoria").all()

        if category_id:
            queryset = queryset.filter(id_categoria=category_id)

        categories = {}
        for produto in queryset:
            categoria = produto.id_categoria
            if categoria.id_categoria not in categories:
                categories[categoria.id_categoria] = {
                    "id": categoria.id_categoria,
                    "nome": categoria.nome_categoria,
                    "icon": categoria.icon,
                    "products": [],
                }

            categories[categoria.id_categoria]["products"].append(ProdutosSerializer(produto).data)

        return Response(list(categories.values()))
