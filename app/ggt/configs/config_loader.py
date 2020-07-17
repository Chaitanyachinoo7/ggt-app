import yaml
import logging
from logging import config
from pathlib import Path

curr_file = Path(__file__)
log_config_file = curr_file.parent.joinpath("log-config.yml")
config_file = curr_file.parent.joinpath("config.yml")


def __init_logging_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        config_data = yaml.safe_load(f.read())
        config.dictConfig(config_data)


def __init_config(path_to_file):
    with open(path_to_file, 'rt') as f:
        cfg = yaml.safe_load(f.read())
        return cfg


#__init_logging_config("./ggt/configs/log-config.yml")
#cfg = __init_config("./ggt/configs/config.yml")

__init_logging_config(log_config_file)
cfg = __init_config(config_file)