"""Module to configure logging"""

from logging.config import dictConfig
from pkg_resources import resource_stream

from pynba.safe_yaml import load


def __configure_logging():
    with resource_stream("pynba", "logging.yaml") as config_file:
        logging_config = load(config_file)
    dictConfig(logging_config)


__configure_logging()
