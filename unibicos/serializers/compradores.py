from rest_framework import serializers

from unibicos.models import Compradores, Usuario
from unibicos.serializers.usuarios import UsuarioSerializer


class CompradoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compradores
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_comprador": obj.id_comprador,
            "id_usuario": UsuarioSerializer(obj.id_usuario).data,
        }
