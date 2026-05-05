from rest_framework import serializers

from unibicos.models import Categorias


class CategoriasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorias
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id": obj.id_categoria,
            "name": obj.nome_categoria,
            "icon": obj.icon,
        }
