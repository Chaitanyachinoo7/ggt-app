from ggt.lib.payment import get_payment_adapter


def bp_create_checkout_session(payment_details):
    # Retrieve the handler and execute the relevant method
    session_handler = get_payment_adapter()
    return session_handler.create_checkout_session(payment_details)


def bp_get_checkout_session(session_id):
    session_handler = get_payment_adapter()
    return session_handler.retrieve_checkout_session(session_id)
