from rest_framework import serializers

from unibicos.models import Movimentacoes


class MovimentacoesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacoes
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_movimentacoes": obj.id_movimentacoes,
            "id_usuario": obj.id_usuario.id,
            "tipo_perfil": obj.tipo_perfil,
            "valor": obj.valor,
        }
