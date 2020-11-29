from pathlib import Path
from jinja2 import (
    Environment, 
    FileSystemLoader, 
    BaseLoader
)

from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.adapters.sendgrid_adapter import (
    send_email as __send_email
)

#TODO: [GGT-95] remove this
#if get_config_val('env') == 'TEST':
#    from ggt.lib.adapters.test_email_adapter import send_email as __send_email


def send_email(from_email, from_name, to_email, subject, html_content, text_content=""):
    return __send_email(from_email, from_name, to_email, subject, html_content, text_content)


def render_template(template, **kwargs):
    ''' renders a Jinja template into HTML from a file'''
    curr_file = Path(__file__)
    template_path = curr_file.parent.parent.joinpath('templates/email/')

    template_loader = FileSystemLoader(searchpath=template_path)
    template_env = Environment(loader=template_loader)
    templ = template_env.get_template(template)
    return templ.render(**kwargs)


def render_from_string(template_string, **kwargs):
    ''' renders a Jinja template into HTML from a string'''
    templ = Environment(loader=BaseLoader).from_string(template_string)
    return templ.render(**kwargs)
