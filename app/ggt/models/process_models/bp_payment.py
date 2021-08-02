from ggt.lib.payment import get_payment_adapter
from ggt.lib.constants import GGT_PAYMENT_FLOW


def bp_create_checkout_session(payment_details, flow=GGT_PAYMENT_FLOW):
    # Retrieve the handler and execute the relevant method
    session_handler = get_payment_adapter()
    return session_handler.create_checkout_session(payment_details, flow)


def bp_get_checkout_session(session_id, flow=GGT_PAYMENT_FLOW):
    session_handler = get_payment_adapter()
    return session_handler.retrieve_checkout_session(session_id, flow)
