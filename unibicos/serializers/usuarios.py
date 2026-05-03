from rest_framework import serializers

from unibicos.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id": obj.id,
            "email": obj.email,
            "id_instituicao": obj.id_instituicao,
            "nome": obj.nome,
            "cpf": obj.cpf,
            "cnpj": obj.cnpj,
            "telefone": obj.telefone,
            "matricula": obj.matricula,
        }
