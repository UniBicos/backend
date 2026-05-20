from rest_framework import serializers

from unibicos.models import Produtos, Categorias, Lojas


class ProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = "__all__"

    def to_representation(self, obj):
        categoria = Categorias.objects.get(id_categoria=obj.id_categoria.id_categoria)
        loja = Lojas.objects.get(id_loja=obj.id_loja.id_loja)
        return {
            "id": obj.id_produto,
            "nome": obj.nome,
            "categoria": {
                "id": categoria.id_categoria,
                "nome": categoria.nome_categoria,
                "icon": categoria.icon,
            },
            "descricao": obj.descricao,
            "preco": obj.preco,
            "imagem": obj.imagem.url if obj.imagem else "",
            "id_loja": obj.id_loja.id_loja,
            "loja": {
                "id": loja.id_loja,
                "nome": loja.nome_fantasia,
                "image": "",  # Ajustar
            },
            "disponivel": obj.disponivel,
        }
