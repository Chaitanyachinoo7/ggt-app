import ggt.lib.adapters.stripe_adapter as stripe_adapter


# This is a factory for payment gateways
def get_payment_adapter(payment_type: str):
    if payment_type == 'stripe':
        return stripe_adapter
    else:
        raise ModuleNotFoundError("Payment adapter not found")
