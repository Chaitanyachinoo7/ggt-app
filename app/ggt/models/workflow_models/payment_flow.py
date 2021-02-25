from ggt.models.process_models.bp_payment import bp_create_checkout_session, bp_get_checkout_session

from ggt.lib.utils import y_response


def payment_create_checkout_session(payment_type, payment_details):
    return y_response(bp_create_checkout_session(payment_type, payment_details))


def payment_get_checkout_session(payment_type, session_id):
    return y_response(bp_get_checkout_session(payment_type, session_id))
