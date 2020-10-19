import yaml
import logging
from logging import config
from pathlib import Path

curr_file = Path(__file__)
print('curr_file:', curr_file)
log_config_file = curr_file.parent.joinpath("log-config.yml")
print('log_config_file:', log_config_file)
config_file = curr_file.parent.joinpath("config.yml")
print('config_file', config_file)


def __init_logging_config(path_to_file):
    print('in __init_logging_config')
    with open(path_to_file, 'rt') as f:
        config_data = yaml.safe_load(f.read())
        print(config_data)
        config.dictConfig(config_data)


def __init_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        cfg = yaml.safe_load(f.read())
        return cfg

__init_logging_config(log_config_file)
cfg = __init_config(config_file)
