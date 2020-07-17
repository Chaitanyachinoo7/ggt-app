import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from ggt.lib.utils import (
    get_config_val,
    log_generic
)



def send_sendgrid_email(from_email, to_email, subject, html_content, text_content=""):
    sendgrid_api_key = get_config_val('sendgrid.sendgrid_api_key')

    sg = SendGridAPIClient(sendgrid_api_key)
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content)

    try:
        response = sg.send(message)
        log_generic(
            type="info", 
            from_email=from_email, 
            to_email=to_email, 
            subject=subject, 
            html_content=html_content, 
            text_content=text_content,
            response_status_code=response.status_code,
            response_body=response.body,
            response_headers=response.headers,
            function='send_sendgrid_email', 
            info='Email Sent')
            
        return True

    except Exception as err:
        log_generic(
            type="error", 
            from_email=from_email, 
            to_email=to_email, 
            subject=subject, 
            html_content=html_content, 
            text_content=text_content,
            function='send_sendgrid_email', 
            error=err
        )

        return False
