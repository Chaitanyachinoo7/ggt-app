from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.adapters.sendgrid_adapter import send_email as __send_email

#if get_config_val('env') == 'TEST':
#    from ggt.lib.adapters.test_email_adapter import send_email as __send_email


def send_email(from_email, from_name, to_email, subject, html_content, text_content=""):
    return __send_email(from_email, from_name, to_email, subject, html_content, text_content)


def render_template(template, **kwargs):
    ''' renders a Jinja template into HTML '''
    import jinja2
    from pathlib import Path
    curr_file = Path(__file__)
    template_path = curr_file.parent.parent.joinpath('templates/email/')

    template_loader = jinja2.FileSystemLoader(searchpath=template_path)
    template_env = jinja2.Environment(loader=template_loader)
    templ = template_env.get_template(template)
    return templ.render(**kwargs)
