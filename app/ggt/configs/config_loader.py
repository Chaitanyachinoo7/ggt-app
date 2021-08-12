import yaml
#import logging
from logging import config
from pathlib import Path

from ggt.lib.adapters.secret_adaptor import get_secret_value

curr_file = Path(__file__)
print('curr_file:', curr_file)
log_config_file = curr_file.parent.joinpath("log-config.yml")
print('log_config_file:', log_config_file)
config_file = curr_file.parent.joinpath("config.yml")
print('config_file', config_file)


def __init_logging_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        config_data = yaml.safe_load(f.read())
        print(config_data)
        config.dictConfig(config_data)


def __init_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        envs = yaml.safe_load(f.read())
        stage = envs['env']
        secret_name = envs['secret_name']
        print('*******************ENVIRONMENT***************** - {}'.format(stage))
        print('*******************SECRET NAME***************** - {}'.format(secret_name))
        return get_secret_value(secret_name, stage)

#__init_logging_config(log_config_file)
cfg = __init_config(config_file)
