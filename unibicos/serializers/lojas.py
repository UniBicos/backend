from rest_framework import serializers

from unibicos.models import Lojas
from unibicos.serializers.usuarios import UsuarioSerializer


class LojasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lojas
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_loja": obj.id_loja,
            "id_usuario": UsuarioSerializer(obj.id_usuario).data,
            "id_bancaria_stripe": obj.id_bancaria_stripe,
            "id_stripe": obj.id_stripe,
            "nome_fantasia": obj.nome_fantasia,
            "aberto": obj.aberto,
            "departamento": obj.departamento,
            "localizacao": obj.localizacao,
            "avaliacao": obj.avaliacao,
        }
