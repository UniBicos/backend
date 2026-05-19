from rest_framework import serializers

from unibicos.models import Entregadores, Usuario
from unibicos.serializers.usuarios import UsuarioSerializer


class EntregadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entregadores
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_entregador": obj.id_entregador,
            "id_usuario": UsuarioSerializer(obj.id_usuario).data,
            "aberto": obj.aberto,
            "saldo_disponivel": obj.saldo_disponivel,
            "avaliacao": obj.avaliacao,
        }
