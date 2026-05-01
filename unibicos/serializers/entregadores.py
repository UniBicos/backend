from rest_framework import serializers

from unibicos.models import Entregadores, Usuario
from unibicos.serializers.usuarios import UsuarioSerializer


class EntregadoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entregadores
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id_entregador': obj.id_entregador,
            'id_usuario': UsuarioSerializer(Usuario.objects.get(user=obj.id_usuario)),
            'info_bancarias': obj.info_bancarias,
            'aberto': obj.aberto,
            'saldo_disponivel': obj.saldo_disponivel,
            'avaliacao': obj.avaliacao,
        }
