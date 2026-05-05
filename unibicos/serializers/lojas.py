from rest_framework import serializers

from unibicos.models import Lojas
from unibicos.serializers.usuarios import UsuarioSerializer


class LojasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lojas
        fields = "__all__"

    def to_representation(self, obj):
        institution_name = (
            obj.id_usuario.id_instituicao.sigla
            if obj.id_usuario and obj.id_usuario.id_instituicao
            else ""
        )
        return {
            "id": obj.id_loja,
            "id_loja": obj.id_loja,
            "userId": obj.id_usuario.id,
            "fantasyName": obj.nome_fantasia,
            "isInformal": False,
            "location": {
                "block": obj.localizacao or "",
                "room": "",
                "reference": "",
            },
            "image": "",
            "rating": obj.avaliacao,
            "institution": institution_name,
            "department": obj.departamento,
        }
