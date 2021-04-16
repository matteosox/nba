"""Module to configure logging"""

from logging.config import dictConfig as __dictConfig
from pkg_resources import resource_stream as __resource_stream

from pynba.safe_yaml import load as __load


def __configure_logging():
    with __resource_stream("pynba", "logging.yaml") as config_file:
        logging_config = __load(config_file)
    __dictConfig(logging_config)


__configure_logging()
