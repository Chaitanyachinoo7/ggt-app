from fastapi import APIRouter, Request, Response, status
from ggt.lib.sms import send_sms
from ggt.lib.email import send_email, render_template
from ggt.models.data_models.data_types import (
    CCSendSMSRequest,
    CCSendEmailRequest,
    CCSendNotiRequest
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


@router.post("/sendemail")
async def api_cc_send_email(CCSendEmailRequest: CCSendEmailRequest):
    try:
        email = formatted_email_message(
            CCSendEmailRequest.first_name, CCSendEmailRequest.token, CCSendEmailRequest.to_email)
        send_email(email["from_email"], email["from_name"],
                   email["to_email"], email["subject"], email["html_content"])
        return {"status": "success"}
    except Exception as err:
        print(err)


@router.post("/sms_email_notify")
async def api_cc_send_sms_email(CCSendNotiRequest: CCSendNotiRequest):
    try:
        email = formatted_email_message(
            CCSendNotiRequest.first_name, CCSendNotiRequest.token, CCSendNotiRequest.to_email)
        send_email(email["from_email"], email["from_name"],
                   email["to_email"], email["subject"], email["html_content"])
        send_sms(CCSendNotiRequest.to_number, formatted_sms_message(
            CCSendNotiRequest.first_name, CCSendNotiRequest.token))
        return {"status": "success"}
    except Exception as err:
        print(err)


def formatted_email_message(first_name, token, to_email):
    base_url = get_config_val('base_url')
    from_email = get_config_val('notifications.from_email')
    from_name = get_config_val('notifications.from_name')
    subject = get_config_val('notifications.result_subject')

    template_vars = {
        "first_name": first_name,
        "result_link": "{}/r/{}".format(base_url, token)
    }

    template_name = get_config_val('notifications.result_template')
    html_content = render_template(template_name, **template_vars)

    email_message = {
        'from_email': from_email,
        'from_name': from_name,
        'to_email': to_email,
        'subject': subject,
        'html_content': html_content
    }

    return email_message
