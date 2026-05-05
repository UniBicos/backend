import stripe

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from unibicos.models import Entregadores
from unibicos.serializers import EntregadoresSerializer


class EntregadoresViewSet(viewsets.ViewSet):
    queryset = Entregadores.objects.all()
    serializer_class = EntregadoresSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Entregadores.objects.all()
        return Response(EntregadoresSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            entregador = Entregadores.objects.get(id_entregador=pk)
        except Entregadores.DoesNotExist:
            return Response({"error": "Entregador não encontrado"}, status=404)

        return Response(EntregadoresSerializer(entregador).data)

    def create(self, request):
        request.data["id_user_cad"] = request.user.id
        user = request.user

        try:
            account = stripe.Account.create(
                type="express",
                country="BR",
                email=user.email,
                business_type="individual",
                business_profile={"name": user.nome},
                metadata={"merchant_name": user.nome},
                controller={
                    "fees": {"payer": "application"},
                    "losses": {"payments": "application"},
                    "stripe_dashboard": {"type": "restricted"},
                    "requirement-collection": "application",
                    "type": "application",
                },
                capabilities={
                    "transfers": {"requested": True},
                },
            )

            bank_account = stripe.Account.create_external_account(
                account.id,
                external_account={
                    "object": "bank_account",
                    "country": "BR",
                    "currency": "brl",
                    "routing_number": f"{request.data.get('codigo_banco')}-{request.data.get('agencia')}",
                    "account_number": request.data.get("conta"),
                },
                default_for_currency=True,
            )

            request.data["id_stripe"] = account.id
            request.data["id_bancaria_stripe"] = bank_account.id
            serializer = EntregadoresSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Entregador cadastrado com sucesso"}, status=201)

            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def partial_update(self, request, pk=None):
        try:
            entregador = Entregadores.objects.get(id_entregador=pk)
        except Entregadores.DoesNotExist:
            return Response({"error": "Entregador não encontrado"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = EntregadoresSerializer(entregador, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Entregador alterado com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, _, pk=None):
        try:
            entregador = Entregadores.objects.get(id_entregador=pk)
        except Entregadores.DoesNotExist:
            return Response({"error": "Entregador não encontrado"}, status=404)

        entregador.delete()
        return Response({"message": "Entregador deletado com sucesso"}, status=204)

    @action(detail=False, methods=["get"])
    def disponiveis(self, _):
        queryset = Entregadores.objects.filter(aberto=True)
        return Response(self.get_serializer(queryset, many=True).data)
