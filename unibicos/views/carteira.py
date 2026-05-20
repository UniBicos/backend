from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Lojas, SaquesLoja
from unibicos.serializers.carteira import (
    SaquesLojaSerializer,
    SolicitarSaqueSerializer,
    calcular_saldo_liberado,
)


class CarteiraViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        id_loja = request.query_params.get("id_loja")
        if not id_loja:
            return Response({"error": "id_loja é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            loja = Lojas.objects.get(id_loja=id_loja)
        except Lojas.DoesNotExist:
            return Response({"error": "Loja não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if loja.id_usuario_id != request.user.id:
            return Response(
                {"error": "Você não tem permissão para visualizar os saques desta loja."},
                status=status.HTTP_403_FORBIDDEN,
            )

        saques = SaquesLoja.objects.filter(id_loja=loja)
        return Response(SaquesLojaSerializer(saques, many=True).data)

    @action(detail=False, methods=["post"], url_path="solicitar_saque")
    def solicitar_saque(self, request):
        serializer = SolicitarSaqueSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        loja_id = serializer.validated_data["loja"].id_loja
        valor = serializer.validated_data["valor"]
        pix = serializer.validated_data["pix"]

        with transaction.atomic():
            loja = Lojas.objects.select_for_update().get(id_loja=loja_id)

            if loja.id_usuario_id != request.user.id:
                return Response(
                    {"error": "Você não tem permissão para solicitar saque desta loja."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            saldo_liberado = calcular_saldo_liberado(loja)
            if valor > saldo_liberado:
                return Response(
                    {
                        "valor": (
                            f"O valor solicitado excede o saldo disponível ({saldo_liberado})."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            saque = SaquesLoja.objects.create(
                id_loja=loja,
                pix=pix,
                valor=valor,
                id_user_cad=request.user,
            )

        return Response(
            {
                "message": "Solicitação de saque registrada com sucesso",
                "saque": SaquesLojaSerializer(saque).data,
            },
            status=status.HTTP_201_CREATED,
        )
