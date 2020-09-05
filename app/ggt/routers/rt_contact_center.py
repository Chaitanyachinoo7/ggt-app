from fastapi import APIRouter, Request, Response, status
from ggt.lib.sms import send_sms
from ggt.lib.email import send_email, render_template
from ggt.models.data_models.data_types import (
    CCSendSMSRequest,
    CCSendEmailRequest,
    CCSendNotiRequest,
    CCOutboundResultRequest
)
from ggt.lib.utils import (
    get_config_val,
    log_generic,
    generate_session_id
)
import boto3
import os
from botocore.config import Config

my_config = Config(
    region_name='us-east-1',
)
os.environ['AWS_ACCESS_KEY_ID'] = 'AKIAR7AATMMMF2D7H352'
os.environ['AWS_SECRET_ACCESS_KEY'] = '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'
client = boto3.client('connect', config=my_config)

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


@router.post("/outbound_result")
def api_cc_outbound_result(CCOutboundResultRequest: CCOutboundResultRequest):
    try:
        result_prompt = ""
        if CCOutboundResultRequest.test_result == "neg":
            result_prompt = "Your test results for sample collected on " + CCOutboundResultRequest.test_date + \
                " were negative, meaning Coronavirus, the virus causing COVID-19, was NOT detected. A negative test means the virus was not present in the sample you provided.   Although your test results did not detect the virus, continue to monitor for symptoms for up to 14 days if you feel you had possible exposure.  This includes Fever, Shortness of Breath or Cough.  You are welcome to get tested again should that happen."
        elif CCOutboundResultRequest.test_result == "pos":
            result_prompt = "Your test results for sample collected on " + CCOutboundResultRequest.test_date + " were positive, meaning Coronavirus, the virus causing COVID-19, WAS detected. A positive test means the virus WAS present in the sample you provided.   Be assured that MOST cases of COVID-19 are MILD and can be treated in your home.  If you are not already doing so, isolate in your home for 14 days.  It is recommended to get others in your home tested as well.  Still, continue to monitor for symptoms for up to 14 days, including chest pain, shortness of breath or cough.  If your symptoms get worse, seek medical care immediately. A GoGetTested provider will also be giving you a call to discuss your symptoms and result and provide a consultation. Please be on the lookout for that call."
        attr = {
            "first_name": CCOutboundResultRequest.first_name,
            "test_date": CCOutboundResultRequest.test_date,
            "dob": CCOutboundResultRequest.dob[5:7] + CCOutboundResultRequest.dob[8:10] + CCOutboundResultRequest.dob[0:4],
            "token": CCOutboundResultRequest.token,
            "to_email": CCOutboundResultRequest.to_email,
            "to_number": CCOutboundResultRequest.to_number,
            "test_result": CCOutboundResultRequest.test_result,
            "greet_message": "Hi, this is GoGetTested.com calling about test results for " + CCOutboundResultRequest.first_name
            + ", who tested on " + CCOutboundResultRequest.test_date + ".",
            "confirm_id_msg": "When " + CCOutboundResultRequest.first_name +
            " is on the line, Press 1. If " + CCOutboundResultRequest.first_name
            + " is not available press 2 or please hang up.",
            "result_prompt": result_prompt
        }
        print(attr)
        client.start_outbound_voice_contact(
            DestinationPhoneNumber=CCOutboundResultRequest.to_number,
            ContactFlowId='e86197ef-25f7-4167-9ed7-daa5fe7faf4b',
            InstanceId='782f4a62-86e8-4674-b5dc-fc88f2d76394',
            SourcePhoneNumber='+18737001872',
            Attributes=attr
        )
        return {"status": "success"}
    except Exception as err:
        print(err)
