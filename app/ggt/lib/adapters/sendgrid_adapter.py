import os

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c


def send_email(from_email, from_name, to_email, subject, html_content, text_content=""):
    sendgrid_api_key = get_config_val('sendgrid.sendgrid_api_key')

    sg = SendGridAPIClient(sendgrid_api_key)
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content)

    try:
        # message.from_email = From('help@twilio.com', 'Twilio SendGrid')
        response = sg.send(message)
        log_generic(
            type=c.INFO,
            from_email=From(from_email, from_name),
            to_email=to_email,
            subject=subject,
            # html_content=html_content,
            text_content=text_content,
            response_status_code=response.status_code,
            response_body=response.body,
            response_headers=response.headers,
            function=whoami(),
            info='Email Sent')

        return True

    except Exception as err:
        log_generic(
            type=c.ERROR,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            function=whoami(),
            error=err
        )

        return False
