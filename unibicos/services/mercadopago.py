# SDK do Mercado Pago
import os

import mercadopago

MP_ACCESS_TOKEN = os.environ.get("MP_ACCESS_TOKEN")

sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
