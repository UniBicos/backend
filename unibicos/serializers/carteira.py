from django.db.models import Sum
from django.utils import timezone
from rest_framework import serializers

from unibicos.models import Lojas, SaquesLoja


class SaquesLojaSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaquesLoja
        fields = "__all__"

    def to_representation(self, obj):
        return {
            "id_saque": obj.id_saque,
            "id_loja": obj.id_loja_id,
            "pix": obj.pix,
            "valor": obj.valor,
            "status": obj.status,
            "dt_cad": obj.dt_cad,
        }


class SolicitarSaqueSerializer(serializers.Serializer):
    id_loja = serializers.IntegerField()
    pix = serializers.CharField(max_length=200)
    valor = serializers.IntegerField()

    def validate_valor(self, value):
        if value <= 0:
            raise serializers.ValidationError("O valor deve ser maior que zero.")
        return value

    def validate_pix(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("A chave PIX é obrigatória.")
        return value

    def validate(self, attrs):
        user = self.context["request"].user

        try:
            loja = Lojas.objects.get(id_loja=attrs["id_loja"])
        except Lojas.DoesNotExist:
            raise serializers.ValidationError({"id_loja": "Loja não encontrada."})

        if loja.id_usuario_id != user.id:
            raise serializers.ValidationError(
                {"id_loja": "Você não tem permissão para solicitar saque desta loja."}
            )

        saldo_liberado = calcular_saldo_liberado(loja)
        if attrs["valor"] > saldo_liberado:
            raise serializers.ValidationError(
                {
                    "valor": (
                        f"O valor solicitado excede o saldo disponível ({saldo_liberado})."
                    )
                }
            )

        today = timezone.localdate()
        if (
            SaquesLoja.objects.filter(id_loja=loja, dt_cad__date=today)
            .exclude(status__in=["CANCELADO", "FALHOU"])
            .exists()
        ):
            raise serializers.ValidationError(
                {"non_field_errors": ["É permitido apenas um saque por dia."]}
            )

        attrs["loja"] = loja
        return attrs


def calcular_saldo_liberado(loja):
    saques_pendentes = (
        SaquesLoja.objects.filter(
            id_loja=loja,
            status__in=["PENDENTE", "PROCESSANDO"],
        ).aggregate(total=Sum("valor"))["total"]
        or 0
    )
    return loja.saldo_disponivel - saques_pendentes
