import ggt.lib.adapters.stripe_adapter as stripe_adapter
from ggt.lib.constants import STRIPE


# This is a factory for payment gateways
def get_payment_adapter(payment_type: str = STRIPE):
    if payment_type == STRIPE:
        return stripe_adapter
    else:
        raise ModuleNotFoundError("Payment adapter not found")
