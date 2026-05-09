import yaml
from logging import config
from pathlib import Path

from ggt.lib.adapters.secret_adaptor import get_secret_value

curr_file = Path(__file__)
log_config_file = curr_file.parent.joinpath("log-config.yml")
config_file = curr_file.parent.joinpath("config.yml")


def __init_logging_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        config_data = yaml.safe_load(f.read())
        config.dictConfig(config_data)


def __init_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        envs = yaml.safe_load(f.read())
        stage = envs['env']
        secret_name = envs['secret_name']
        if stage == 'LOCAL':
            return envs
        else:
            return get_secret_value(secret_name)

#__init_logging_config(log_config_file)
cfg = __init_config(config_file)
