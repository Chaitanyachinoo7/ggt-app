from ggt.lib.utils import get_config_val as cfg
from ggt.lib.adapters.sendgrid_adapter import send_email
from ggt.lib.email import render_template


def send_new_account_registration_request_email(first_name, email):
    from_email = cfg('notifications.from_email_ggd')
    from_name = cfg('notifications.from_name_ggd')
    subject = "GoGetVax provider account creation request received"
    template_vars = {
        "first_name": first_name
    }
    template_name = 'GGV-2-NEW_ACCOUNT_REQUEST-EMAIL.html'
    html_content = render_template(template_name, **template_vars)
    send_email(from_email, from_name, email, subject, html_content)


def send_new_account_creation_email(first_name, email, password, org=False):
    from_email = cfg('notifications.from_email_ggd')
    from_name = cfg('notifications.from_name_ggd')
    portal_url = cfg('portal_url')
    ops_url = cfg('ops_url')
    subject = "GoGetTested Account created"
    template_vars = {
        "first_name": first_name,
        "portal_url": portal_url,
        "ops_url": ops_url,
        "email": email,
        "password": password,
        "hide_phone_number": True
    }
    if org:
        template_name = 'GGV-3-NEW_ACCOUNT-EMAIL.html'
    else:
        template_name = 'GGT-19-NEW_ACCOUNT-EMAIL.html'
    html_content = render_template(template_name, **template_vars)
    send_email(from_email, from_name, email, subject, html_content)


def send_org_reject_email(first_name, email):
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    subject = "GoGetTested Account created"
    template_vars = {
        "first_name": first_name
    }
    template_name = 'GGT-20-REJECT_ACCOUNT-EMAIL.html'
    html_content = render_template(template_name, **template_vars)
    send_email(from_email, from_name, email, subject, html_content)
