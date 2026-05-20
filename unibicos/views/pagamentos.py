from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.db import transaction

from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_http_methods
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from unibicos.models import Pagamento, Pedidos
from unibicos.serializers import PagamentoSerializer
from unibicos.services.mercadopago import sdk


def _normalize_unit_price(value):
    if value is None:
        raise InvalidOperation("Valor ausente")
    return float(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _map_mp_status(status):
    if status in {"approved", "authorized"}:
        return "CONFIRMADO"
    if status in {"pending", "in_process", "in_mediation"}:
        return "AGUARDANDO_PAGAMENTO"
    if status in {"rejected", "cancelled", "charged_back", "refunded"}:
        return "CANCELADO"
    return None


class PagamentoViewSet(viewsets.ViewSet):
    queryset = Pagamento.objects.all()
    serializer_class = PagamentoSerializer
    permission_classes = [AllowAny]

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
        id_pedido = request.data.get("id_pedido")
        if not id_pedido:
            return Response({"error": "id_pedido é obrigatório"}, status=400)

        try:
            pedido = Pedidos.objects.get(id_pedido=id_pedido)
        except Pedidos.DoesNotExist:
            return Response({"error": "Pedido não encontrado"}, status=404)

        with transaction.atomic():
            pagamento, created = Pagamento.objects.get_or_create(
                id_pedido=pedido, defaults={"status_pagamento": "AGUARDANDO_PAGAMENTO"}
            )

            if pagamento.status_pagamento != "AGUARDANDO_PAGAMENTO":
                return Response({"error": "Pagamento não pode ser iniciado"}, status=409)

            if pagamento.id_intent:
                return Response({"error": "Pagamento já iniciado"}, status=409)

            valor_total = pedido.total_pedido
            try:
                unit_price = _normalize_unit_price(valor_total)
            except (InvalidOperation, TypeError, ValueError):
                return Response({"error": "Valor inválido"}, status=400)

            title = request.data.get("title") or f"Pedido #{pedido.id_pedido}"
            return_url = request.build_absolute_uri(reverse("mercadopago_return"))
            back_urls = request.data.get("back_urls") or {
                "success": return_url,
                "failure": return_url,
                "pending": return_url,
            }

            for key in ("success", "failure", "pending"):
                if not back_urls.get(key):
                    back_urls[key] = return_url

            try:
                preference_data = {
                    "items": [
                        {
                            "title": title,
                            "quantity": 1,
                            "unit_price": unit_price,
                        }
                    ],
                    "back_urls": back_urls,
                    "auto_return": "approved",
                    "external_reference": str(pedido.id_pedido),
                }

                preference_response = sdk.preference().create(preference_data)
                preference = preference_response.get("response", {})
                preference_id = preference.get("id")
                if not preference_id:
                    return Response({"error": "Falha ao criar preferência"}, status=400)

                pagamento.id_intent = preference_id
                pagamento.save()

                return Response(
                    {
                        "preference_id": preference_id,
                        "init_point": preference.get("init_point"),
                        "sandbox_init_point": preference.get("sandbox_init_point"),
                        "message": "Pagamento iniciado com sucesso",
                    },
                    status=201,
                )

            except Exception as e:
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


@require_http_methods(["GET"])
def mercadopago_return(request):
    status = request.GET.get("status") or request.GET.get("collection_status")
    payment_id = request.GET.get("payment_id") or request.GET.get("collection_id")
    preference_id = request.GET.get("preference_id")
    external_reference = request.GET.get("external_reference")

    pagamento = None
    if preference_id:
        pagamento = Pagamento.objects.filter(id_intent=preference_id).first()
    if not pagamento and external_reference:
        pagamento = Pagamento.objects.filter(id_pedido__id_pedido=external_reference).first()

    if not pagamento:
        return JsonResponse({"error": "Pagamento não encontrado"}, status=404)

    mapped_status = _map_mp_status(status)
    if mapped_status and pagamento.status_pagamento != mapped_status:
        pagamento.status_pagamento = mapped_status
        pagamento.save()

    pedido = pagamento.id_pedido
    if mapped_status == "CONFIRMADO" and pedido.status_pedido != "ACEITO_PELO_VENDEDOR":
        pedido.status_pedido = "ACEITO_PELO_VENDEDOR"
        pedido.save()
    elif mapped_status == "CANCELADO" and pedido.status_pedido != "CANCELADO":
        pedido.status_pedido = "CANCELADO"
        pedido.save()

    return JsonResponse(
        {
            "status": status,
            "mapped_status": mapped_status,
            "payment_id": payment_id,
            "preference_id": preference_id,
            "external_reference": external_reference,
        }
    )
