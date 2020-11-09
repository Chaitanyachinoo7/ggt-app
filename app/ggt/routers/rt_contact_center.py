import os

import boto3
from botocore.config import Config
from fastapi import (
    APIRouter, 
    Depends, 
    HTTPException, 
    Security
)
from ggt.lib.auth import authorise_user
from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    AUTH_FAILED_MESSAGE
)
from ggt.lib.email import send_email, render_template
from ggt.lib.sms import send_sms
from ggt.lib.utils import (
    get_config_val,
    is_contact_center
)
from ggt.models.data_models.data_types import (
    CCSendSMSRequest,
    CCSendEmailRequest,
    CCSendNotiRequest,
    CCOutboundResultRequest,
    CCOutboundResultStatusRequest,
    User, 
    PermissionsEnum as p
)
from ggt.models.workflow_models.contact_center_flow import (
    cc_update_outbound_call_status
)

my_config = Config(
    region_name='us-east-1',
)
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAR7AATMMMF2D7H352'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
client = boto3.client('connect', config=my_config)

router = APIRouter()


def formatted_sms_message(first_name, token):
    base_url = get_config_val('base_url')
    return "Hi {}, your GoGetTested.com COVID-19 test results are available. Please follow this link to view your " \
           "results {}/r/{}".format(first_name, base_url, token)


@router.post("/sendsms", dependencies=[Security(authorise_user, scopes=[p.SENDSMS])])
async def api_cc_send_sms(CCSendSMSRequest: CCSendSMSRequest):
    try:
        send_sms(CCSendSMSRequest.to_number, formatted_sms_message(
            CCSendSMSRequest.first_name, CCSendSMSRequest.token))
        return {STATUS: SUCCESS}
    except Exception as err:
        print(err)


@router.post("/sendemail", dependencies=[Security(authorise_user, scopes=[p.SENDEMAIL])])
async def api_cc_send_email(CCSendEmailRequest: CCSendEmailRequest):
    try:
        email = formatted_email_message(
            CCSendEmailRequest.first_name, CCSendEmailRequest.token, CCSendEmailRequest.to_email)
        send_email(email["from_email"], email["from_name"],
                   email["to_email"], email["subject"], email["html_content"])
        return {STATUS: SUCCESS}
    except Exception as err:
        print(err)


@router.post("/sms_email_notify", dependencies=[Security(authorise_user, scopes=[p.SMS_EMAIL_NOTIFY])])
async def api_cc_send_sms_email(CCSendNotiRequest: CCSendNotiRequest):
    try:

        email = formatted_email_message(
            CCSendNotiRequest.first_name, CCSendNotiRequest.token, CCSendNotiRequest.to_email)
        send_email(email["from_email"], email["from_name"],
                   email["to_email"], email["subject"], email["html_content"])
        send_sms(CCSendNotiRequest.to_number, formatted_sms_message(
            CCSendNotiRequest.first_name, CCSendNotiRequest.token))
        return {STATUS: SUCCESS}

    except Exception as err:
        print(err)


@router.post("/outbound_result_status", dependencies=[Security(authorise_user, scopes=[p.OUTBOUND_RESULT_STATUS])])
def outbound_result_status(CCOutboundResultStatusRequest: CCOutboundResultStatusRequest):
    try:
        cc_update_outbound_call_status(
            CCOutboundResultStatusRequest.test_id,
            CCOutboundResultStatusRequest.first_name,
            CCOutboundResultStatusRequest.test_date,
            CCOutboundResultStatusRequest.dob,
            CCOutboundResultStatusRequest.token,
            CCOutboundResultStatusRequest.to_email,
            CCOutboundResultStatusRequest.to_number,
            CCOutboundResultStatusRequest.test_result,
            CCOutboundResultStatusRequest.call_status
        )
    except Exception as err:
        print(err)
