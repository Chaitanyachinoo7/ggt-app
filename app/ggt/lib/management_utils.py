from ggt.lib.utils import get_config_val as cfg
from ggt.lib.adapters.sendgrid_adapter import send_email
from ggt.lib.email import render_template


def send_new_account_creation_email(first_name, email, password):
    from_email = cfg('notifications.from_email')
    from_name = cfg('notifications.from_name')
    subject = "GoGetTested Account created"
    template_vars = {
        "first_name": first_name,
        "email": email,
        "password": password
    }
    template_name = 'GGT-19-NEW_ACCOUNT-EMAIL.html'
    html_content = render_template(template_name, **template_vars)
    send_email(from_email, from_name, email, subject, html_content)
