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
            "id_usuario": UsuarioSerializer(Usuario.objects.get(user=obj.id_usuario)),
            "id_bancaria_stripe": obj.id_bancaria_stripe,
            "id_stripe": obj.id_stripe,
            "aberto": obj.aberto,
            "saldo_disponivel": obj.saldo_disponivel,
            "avaliacao": obj.avaliacao,
        }
