from rest_framework import serializers

from unibicos.models import Lojas, Usuario
from unibicos.serializers.usuarios import UsuarioSerializer


class LojasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lojas
        fields = '__all__'

    def to_representation(self, obj):
        return {
            'id_loja': obj.id_loja,
            'id_usuario': UsuarioSerializer(Usuario.objects.get(user=obj.id_usuario)),
            'info_bancarias': obj.info_bancarias,
            'nome_fantasia': obj.nome_fantasia,
            'aberto': obj.aberto,
            'departamento': obj.departamento,
            'localizacao': obj.localizacao,
            'avaliacao': obj.avaliacao,
        }
