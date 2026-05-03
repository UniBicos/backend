from rest_framework import serializers

from unibicos.models import Produtos, Categorias, Lojas


class ProdutosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produtos
        fields = '__all__'

    def to_representation(self, obj):
        categoria = Categorias.objects.get(id_categoria=obj.id_categoria.id_categoria)
        loja = Lojas.objects.get(id_loja=obj.id_loja.id_loja)
        return {
            'id': obj.id_produto,
            'title': obj.nome_produto,
            'categoryId': obj.id_categoria.id_categoria,
            'category': {
                'id': categoria.id_categoria,
                'name': categoria.nome_categoria,
                'icon': categoria.icon,
            },
            'description': obj.descricao,
            'price': obj.preco,
            'image': obj.imagem.url if obj.imagem else '',
            'sellerId': obj.id_loja.id_loja,
            'isAvailable': obj.disponivel,
        }
