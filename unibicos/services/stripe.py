import stripe

from core.settings import STRIPE_SECRET_KEY

stripe.api_key = STRIPE_SECRET_KEY

__all__ = ["stripe"]
