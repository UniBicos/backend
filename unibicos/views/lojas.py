from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from unibicos.models import Lojas, Produtos
from unibicos.serializers import LojasSerializer, ProdutosSerializer
from unibicos.views import stripe


class LojasViewSet(viewsets.ViewSet):
    queryset = Lojas.objects.all()
    serializer_class = LojasSerializer
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = Lojas.objects.all()
        return Response(LojasSerializer(queryset, many=True).data)

    def retrieve(self, request, pk=None):
        try:
            loja = Lojas.objects.get(id_loja=pk)
        except Lojas.DoesNotExist:
            return Response({"error": "Loja não encontrada"}, status=404)

        produtos = Produtos.objects.filter(id_loja=loja.id_loja)
        data = LojasSerializer(loja).data
        data['products'] = ProdutosSerializer(produtos, many=True).data
        return Response(data)

    def create(self, request):
        request.data["id_user_cad"] = request.user.id
        user = request.user

        try:
            account = stripe.Account.create(
                type="express",
                country="BR",
                email=user.email,
                business_type=(
                    "individual"
                    if request.data.get("tipo_pessoa") == "fisica"
                    else "company"
                ),
                controller={
                    "fees": {"payer": "application"},
                    "losses": {"payments": "application"},
                    "stripe_dashboard": {"type": "restricted"},
                },
                capabilities={
                    "card_payments": {"requested": True},
                    "transfers": {"requested": True},
                },
                business_profile={"name": request.data.get("nome_fantasia")},
                metadata={"merchant_name": user.nome},
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
            serializer = LojasSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Loja cadastrada com sucesso"}, status=201)

            return Response(serializer.errors, status=400)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

    def partial_update(self, request, pk=None):
        try:
            loja = Lojas.objects.get(id_loja=pk)
        except Lojas.DoesNotExist:
            return Response({"error": "Loja não encontrada"}, status=404)

        request.data["id_user_alt"] = request.user.id
        serializer = LojasSerializer(loja, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Loja alterada com sucesso"})
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        try:
            loja = Lojas.objects.get(id_loja=pk)
        except Lojas.DoesNotExist:
            return Response({"error": "Loja não encontrada"}, status=404)

        loja.delete()
        return Response({"message": "Loja deletada com sucesso"}, status=204)
