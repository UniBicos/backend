from rest_framework import serializers

from unibicos.models import Produtos


class ProdutosSerializer(serializers.ModelSerializer):

    class Meta:
        model = Produtos
        fields = '__all__'

    def to_representation(self, obj):
        res = {
            'id_produto': obj.id_produto,
            'id_loja': obj.id_loja.id_loja,
            'id_categoria': obj.id_categoria.id_categoria,
            'nome_produto': obj.nome_produto,
            'imagem': obj.imagem.url if obj.imagem else None,
            'descricao': obj.descricao,
            'preco': obj.preco,
            'disponivel': obj.disponivel,
        }

        return res
