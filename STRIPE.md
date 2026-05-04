# Stripe Webhook Setup Guide

## Overview

This document covers the complete Stripe webhook implementation for the marketplace payment system.

## Database Migrations

The following fields have been added to support the webhook system:

### 1. Lojas Model

- **Field Added**: `saldo_disponivel` (IntegerField, default=0)
- **Purpose**: Track vendor balance from successful payments

**Migration Command**:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Entregadores Model

- **Field Added**: `id_stripe` (CharField, max_length=200, unique=True)
- **Purpose**: Store Stripe connected account ID for deliverer

## Settings Configuration

Add to your `settings.py`:

```python
# Stripe Configuration
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET")

# Payment Distribution (percentages)
STRIPE_VENDOR_PERCENTAGE = 0.80      # 80% to vendor
STRIPE_DELIVERER_PERCENTAGE = 0.10   # 10% to deliverer
STRIPE_PLATFORM_FEE_PERCENTAGE = 0.10  # 10% platform fee
```

## Environment Variables

Create or update your `.env` file:

```env
STRIPE_SECRET_KEY=sk_live_xxxxxxxxxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxxxxxxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxx
```

**To get these values:**

1. Go to [Stripe Dashboard](https://dashboard.stripe.com)
2. Navigate to Developers > API Keys for secret/publishable keys
3. Navigate to Developers > Webhooks for webhook secret

## URL Configuration

The webhook endpoint is registered in `urls.py`:

```
POST /webhook/stripe/
```

**Full URL example**: `https://yourdomain.com/webhook/stripe/`

## Testing Locally

### Option 1: Using Stripe CLI

```bash
# Install Stripe CLI
# https://stripe.com/docs/stripe-cli

# Login to your Stripe account
stripe login

# Forward webhook events to localhost
stripe listen --forward-to localhost:8000/webhook/stripe/

# This will output your webhook signing secret
# Add it to STRIPE_WEBHOOK_SECRET in settings
```

### Option 2: Using ngrok

```bash
# Start ngrok tunnel
ngrok http 8000

# Your public URL will be: https://xxxx-xx-xxx-xxx-xx.ngrok.io
# Webhook endpoint: https://xxxx-xx-xxx-xxx-xx.ngrok.io/webhook/stripe/

# Add webhook in Stripe Dashboard pointing to this URL
```

## Webhook Events Handled

### 1. **payment_intent.succeeded**

Triggers when a payment is successfully completed:

- Updates `Pagamento.status_pagamento` → "PAGO" → "CONFIRMADO"
- Updates `Pedidos.status_pedido` → "ACEITO_PELO_VENDEDOR"
- Creates transfers to vendor (80%) and deliverer (10%)
- Updates `Lojas.saldo_disponivel` and `Entregadores.saldo_disponivel`

### 2. **payment_intent.payment_failed**

Triggers when payment fails:

- Updates `Pagamento.status_pagamento` → "CANCELADO"
- Updates `Pedidos.status_pedido` → "CANCELADO"

### 3. **charge.dispute.created**

Triggers when a chargeback/dispute is created:

- Updates `Pagamento.status_pagamento` → "CANCELADO"
- Updates `Pedidos.status_pedido` → "CANCELADO"
- Logs dispute for review

## Payment Flow

```
1. Client initiates payment
   ↓
2. PaymentIntent created in pagamentos.py
   ↓
3. Frontend completes payment with PIX QR code
   ↓
4. Stripe confirms payment
   ↓
5. Webhook triggers: payment_intent.succeeded
   ↓
6. Database updated with payment status
   ↓
7. Transfers created to vendor & deliverer accounts
   ↓
8. Order status updated
   ↓
9. Available balance updated for both parties
```

## Logging

Webhook events and errors are logged to `logging` module:

```python
import logging
logger = logging.getLogger(__name__)
# Logs appear in Django console and configured log files
```

## Error Handling

All exceptions are caught and logged:

- Signature verification errors (security)
- Missing payment in database
- Stripe API errors
- Database transaction errors

Failed webhook processing returns HTTP 500 to trigger Stripe retry.

## Database Constraints

### Pagamento Model

- `id_stripe` (unique): Payment Intent ID from Stripe
- `status_pagamento` (choices): AGUARDANDO_PAGAMENTO, PAGO, CONFIRMADO, CANCELADO

### Lojas Model

- `id_stripe` (unique): Stripe Connect Account ID
- `saldo_disponivel`: Running balance from payments

### Entregadores Model

- `id_stripe` (unique): Stripe Connect Account ID
- `saldo_disponivel`: Running balance from deliveries

## Testing Webhook Events

### Using Stripe Dashboard

1. Go to Developers > Webhooks
2. Click on your endpoint
3. Click "Send test event"
4. Select event type (e.g., `payment_intent.succeeded`)
5. Review webhook delivery history

### Using Stripe CLI

```bash
# Simulate payment success
stripe trigger payment_intent.succeeded

# Simulate payment failure
stripe trigger payment_intent.payment_failed

# Simulate dispute
stripe trigger charge.dispute.created
```

## Troubleshooting

### 1. Webhook Not Receiving Events

- Verify endpoint URL is publicly accessible
- Check webhook signing secret matches
- Verify firewall/CORS allows POST requests
- Check Django CSRF exemption (already in place)

### 2. Payment Status Not Updating

- Check logs: `logger.error()` entries
- Verify `Pagamento` record exists with correct `id_stripe`
- Check database migration was applied
- Verify Stripe API key is valid

### 3. Transfers Not Created

- Check vendor/deliverer IDs in payment metadata
- Verify Stripe connected accounts are in good standing
- Check transfer amounts are valid (not zero)
- Review Stripe API response in logs

### 4. Balance Not Updating

- Ensure `saldo_disponivel` field exists in database
- Check transaction is not rolling back
- Verify permissions on model save
