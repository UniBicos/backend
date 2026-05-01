from pytz import timezone

import stripe
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from unibicos.models import Pagamento
from unibicos.serializers import PagamentoSerializer


class PagamentoViewSet(viewsets.ViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Pagamento.objects.all()
        return Response(PagamentoSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            pagamento = Pagamento.objects.get(id_pagamento=pk)
        except Pagamento.DoesNotExist:
            return Response({"error": "Pagamento não encontrado"}, status=404)

        return Response(PagamentoSerializer(pagamento).data)

    def create(self, request):
        # 1. Pegar dados do pedido
        valor_total = request.data.get("valor")
        id_vendedor_stripe = request.data.get("id_vendedor_stripe")
        id_entregador_stripe = request.data.get("id_entregador_stripe")
        amount = int(float(valor_total) * 100)
        application_fee = int(amount * 0.1)
        try:
            # 2. Criar o Intent no Stripe
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency="brl",
                payment_method_types=["pix"],
                transfer_group=f"ORDER_{request.user.id}_{timezone.now().timestamp()}",
                application_fee_amount=application_fee,
                metadata={
                    "user_id": request.user.id,
                    "vendedor_id": id_vendedor_stripe,
                    "entregador_id": id_entregador_stripe,
                },
            )

            # 3. Salvar no seu banco de dados
            pagamento_data = {
                "id_user": request.user.id,
                "valor": valor_total,
                "id_intent": intent.id,
                "status": "pendente",
            }

            serializer = PagamentoSerializer(data=pagamento_data)
            if serializer.is_valid():
                serializer.save()

                # 4. Retornar o necessário para o Frontend gerar o QR Code
                return Response(
                    {
                        "client_secret": intent.client_secret,
                        "id_intent": intent.id,
                        "message": "Pagamento iniciado com sucesso",
                    },
                    status=201,
                )

            return Response(serializer.errors, status=400)

        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=400)

    def partial_update(self, request, pk=None):
        try:
            pagamento = Pagamento.objects.get(id_pagamento=pk)
        except Pagamento.DoesNotExist:
            return Response({"error": "Pagamento não encontrado"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = PagamentoSerializer(pagamento, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Pagamento alterado com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            pagamento = Pagamento.objects.get(id_pagamento=pk)
        except Pagamento.DoesNotExist:
            return Response({"error": "Pagamento não encontrado"}, status=404)

        pagamento.delete()
        return Response(status=204)
