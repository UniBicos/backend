from rest_framework import serializers

from unibicos.models import EmailsInstituicao, InstituicoesEnsino


class EmailsInstituicaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailsInstituicao
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_email_instituicao": obj.id_email_instituicao,
            "id_instituicao": obj.id_instituicao.id_instituicao,
            "email": obj.email,
        }


class InstituicoesEnsinoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstituicoesEnsino
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_instituicao": obj.id_instituicao,
            "nome": obj.nome,
            "sigla": obj.sigla,
            "campus": obj.campus,
            "cidade": obj.cidade,
            "estado": obj.estado,
            "emaisl": EmailsInstituicaoSerializer(
                EmailsInstituicao.objects.filter(id_instituicao=obj.id_instituicao), many=True
            ).data,
        }
