from rest_framework import serializers

from unibicos.models import Lojas
from unibicos.serializers.instituicoes_ensino import InstituicoesEnsinoSerializer


class LojasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lojas
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id": obj.id_loja,
            "id_usuario": obj.id_usuario.id,
            "nome_fantasia": obj.nome_fantasia,
            "informal": obj.cnpj == "",
            "localizacao": obj.localizacao,
            "imagem": "",
            "avaliacao": obj.avaliacao,
            "instituicao": (
                InstituicoesEnsinoSerializer(obj.id_usuario.id_instituicao).data
                if obj.id_usuario and obj.id_usuario.id_instituicao
                else None
            ),
            "departamento": obj.departamento,
        }
