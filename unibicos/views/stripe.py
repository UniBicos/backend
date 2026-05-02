import logging
import stripe
from decimal import Decimal
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.db import transaction
from unibicos.models import Pagamento, Pedidos, Lojas, Entregadores

logger = logging.getLogger(__name__)

# Configurar chave API Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

# Constantes de divisão de pagamento (em porcentagem)
VENDOR_PERCENTAGE = 0.80  # 80% para o vendedor
DELIVERER_PERCENTAGE = 0.10  # 10% para o entregador
PLATFORM_FEE_PERCENTAGE = 0.10  # 10% para a plataforma


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """
    Webhook handler para eventos Stripe.
    Processa pagamentos, transferências e disputas.
    """
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return HttpResponse(status=400)

    logger.info(f"Received event: {event['type']}")

    try:
        if event["type"] == "payment_intent.succeeded":
            handle_payment_succeeded(event["data"]["object"])

        elif event["type"] == "payment_intent.payment_failed":
            handle_payment_failed(event["data"]["object"])

        elif event["type"] == "charge.dispute.created":
            handle_dispute_created(event["data"]["object"])

    except Exception as e:
        logger.error(f"Error processing event: {str(e)}", exc_info=True)
        return HttpResponse(status=500)

    return HttpResponse(status=200)


@transaction.atomic
def handle_payment_succeeded(payment_intent):
    """
    Processa pagamento bem-sucedido:
    1. Atualiza status do pagamento
    2. Atualiza status do pedido
    3. Cria transferências para vendedor e entregador
    """
    try:
        pagamento = Pagamento.objects.get(id_stripe=payment_intent["id"])
    except Pagamento.DoesNotExist:
        logger.error(f"Payment not found: {payment_intent['id']}")
        return

    # Já processado
    if pagamento.status_pagamento == "CONFIRMADO":
        logger.info(f"Payment already processed: {payment_intent['id']}")
        return

    try:
        # 1. Atualizar status do pagamento
        pagamento.status_pagamento = "PAGO"
        pagamento.save()

        # 2. Atualizar status do pedido
        pedido = pagamento.id_pedido
        pedido.status_pedido = "ACEITO_PELO_VENDEDOR"
        pedido.save()

        # 3. Executar split de pagamento
        metadata = payment_intent.get("metadata", {})
        vendedor_stripe_id = metadata.get("vendedor_id")
        entregador_stripe_id = metadata.get("entregador_id")
        valor_total = payment_intent["amount"]  # em centavos

        if not vendedor_stripe_id or not entregador_stripe_id:
            logger.error(f"Missing vendor or deliverer ID in metadata: {metadata}")
            return

        # Calcular montantes (em centavos)
        valor_vendedor = int(valor_total * VENDOR_PERCENTAGE)
        valor_entregador = int(valor_total * DELIVERER_PERCENTAGE)
        taxa_plataforma = valor_total - valor_vendedor - valor_entregador

        # Criar transferências
        transfer_group = payment_intent["transfer_group"]

        # Transferência para vendedor
        vendor_transfer = stripe.Transfer.create(
            amount=valor_vendedor,
            currency="brl",
            destination=vendedor_stripe_id,
            transfer_group=transfer_group,
            metadata={"pedido_id": str(pedido.id_pedido), "tipo": "vendor"},
        )
        logger.info(f"Vendor transfer created: {vendor_transfer['id']}")

        # Transferência para entregador
        deliverer_transfer = stripe.Transfer.create(
            amount=valor_entregador,
            currency="brl",
            destination=entregador_stripe_id,
            transfer_group=transfer_group,
            metadata={"pedido_id": str(pedido.id_pedido), "tipo": "deliverer"},
        )
        logger.info(f"Deliverer transfer created: {deliverer_transfer['id']}")

        # 4. Atualizar saldos disponíveis na plataforma
        try:
            loja = Lojas.objects.get(id_stripe=vendedor_stripe_id)
            loja.saldo_disponivel = (loja.saldo_disponivel or 0) + valor_vendedor
            loja.save()
            logger.info(f"Updated vendor balance: {loja.id_loja}")
        except Lojas.DoesNotExist:
            logger.warning(f"Vendor not found: {vendedor_stripe_id}")

        try:
            entregador = Entregadores.objects.get(id_stripe=entregador_stripe_id)
            entregador.saldo_disponivel = (
                entregador.saldo_disponivel or 0
            ) + valor_entregador
            entregador.save()
            logger.info(f"Updated deliverer balance: {entregador.id_entregador}")
        except Entregadores.DoesNotExist:
            logger.warning(f"Deliverer not found: {entregador_stripe_id}")

        # 5. Confirmar pagamento
        pagamento.status_pagamento = "CONFIRMADO"
        pagamento.save()

        logger.info(
            f"Payment {payment_intent['id']} processed successfully. "
            f"Vendor: {valor_vendedor}, Deliverer: {valor_entregador}, Platform: {taxa_plataforma}"
        )

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error processing payment: {str(e)}")
        pagamento.status_pagamento = "CANCELADO"
        pagamento.save()
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing payment: {str(e)}", exc_info=True)
        pagamento.status_pagamento = "CANCELADO"
        pagamento.save()
        raise


@transaction.atomic
def handle_payment_failed(payment_intent):
    """
    Processa pagamento falhado.
    """
    try:
        pagamento = Pagamento.objects.get(id_stripe=payment_intent["id"])
        pagamento.status_pagamento = "CANCELADO"
        pagamento.save()

        # Atualizar status do pedido também
        pedido = pagamento.id_pedido
        pedido.status_pedido = "CANCELADO"
        pedido.save()

        logger.warning(
            f"Payment failed: {payment_intent['id']} - {payment_intent.get('last_payment_error', {}).get('message')}"
        )

    except Pagamento.DoesNotExist:
        logger.error(f"Payment not found: {payment_intent['id']}")
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}", exc_info=True)


def handle_dispute_created(charge):
    """
    Processa disputa/chargeback.
    """
    try:
        dispute_id = charge.get("dispute")
        if not dispute_id:
            return

        logger.warning(f"Dispute created: {dispute_id} for charge {charge['id']}")

        # Tentar encontrar o pagamento relacionado
        try:
            pagamento = Pagamento.objects.get(id_stripe=charge["payment_intent"])
            pagamento.status_pagamento = "CANCELADO"
            pagamento.save()

            pedido = pagamento.id_pedido
            pedido.status_pedido = "CANCELADO"
            pedido.save()

            logger.info(
                f"Updated payment and order status due to dispute: {dispute_id}"
            )
        except Pagamento.DoesNotExist:
            logger.warning(f"Payment not found for dispute: {dispute_id}")

    except Exception as e:
        logger.error(f"Error handling dispute: {str(e)}", exc_info=True)


# CLI: stripe listen --forward-to localhost:8000/webhook/stripe
# Configurar em settings.py:
# STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
# STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")
