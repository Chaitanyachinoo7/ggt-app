import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl
ssl._create_default_https_context = ssl._create_unverified_context



def send_sendgrid_email(from_email, to_email, subject, html_content, text_content=""):
    sendgrid_api_key = "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"
    
    sg = SendGridAPIClient(sendgrid_api_key)
    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=html_content)

    try:
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)

    except Exception as err:
        # print(e.message)zz
        print("sending-email-failed: {}".format(err))
        print("from: {} / to: {} / subject: {} / html_content: {} / text_content: {};".format(from_email, to_email, subject, html_content, text_content))
        return False


def render_template(template_folder, template, **kwargs):
    ''' renders a Jinja template into HTML '''
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    template_path = file_dir + "/templates/email/"

    # check if template exists
    if not os.path.exists(template_path):
        print("No template file present: {} / path: {}".format(template, template_path))
        return None


    import jinja2    
    template_loader = jinja2.FileSystemLoader(searchpath=template_path)
    template_env = jinja2.Environment(loader=template_loader)
    templ = template_env.get_template(template)
    return templ.render(**kwargs)



def send_email(from_email, to_email, subject, html_content, text_content=""):
    return send_sendgrid_email(from_email, to_email, subject, html_content, text_content)


# MAIN
template_vars = {
        "first_name": "first_name",
        "email": "email",
        "password": "password"
    }


# generate HTML from template
template_folder = "/templates/email/"
template_name = 'GGT-19-NEW_ACCOUNT-EMAIL.html'
html_content = render_template(template_folder, template_name, **template_vars)

from_email = "support@gogettested.com"
to_email = "visithamanujaya@gmail.com"
subject = "COVID-19 Testing Appointment Confirmation"

send_email(from_email, to_email, subject, html_content)
