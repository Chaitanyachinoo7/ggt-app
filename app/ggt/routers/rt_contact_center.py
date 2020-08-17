from fastapi import APIRouter, Request, Response, status
from ggt.lib.sms import send_sms
from ggt.models.data_models.data_types import (
    CCSendSMSRequest
)
from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)
router = APIRouter()


def formatted_sms_message(first_name, token):
    base_url = get_config_val('base_url')
    return "Hi {}, your GoGetTested.com COVID-19 test results are available. Please follow this link to view your results {}/r/{}".format(first_name, base_url, token)


@router.post("/sendsms")
async def api_cc_send_sms(CCSendSMSRequest: CCSendSMSRequest):
    try:
        send_sms(CCSendSMSRequest.to_number, formatted_sms_message(
            CCSendSMSRequest.first_name, CCSendSMSRequest.token))
        return {"status": "success"}
    except Exception as err:
        print(err)
