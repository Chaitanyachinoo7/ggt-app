from fastapi import APIRouter
from ggt.models.workflow_models.payment_flow import payment_create_checkout_session, payment_get_checkout_session
from ggt.models.data_models.data_types import PaymentRequestBody

router = APIRouter()


# This route create a checkout session, that FE uses to redirect to the relevant payment gateway
@router.post("/checkout/sessions")
def api_payment_checkout_session(payment_details: PaymentRequestBody):
    return payment_create_checkout_session(payment_details)


# This route will provide details on the status of the session
@router.get("/checkout/sessions/{session_id}")
def api_payment_session_id(session_id: str):
    return payment_get_checkout_session(session_id)

