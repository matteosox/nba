"""Hodge podge of NBA stats and analysis utilities"""

from pkg_resources import resource_stream

from pynba.load_parsed_data import load_games
from pynba.plot_logos import plot_logos
from pynba.teams import *


def __get_version():
    with resource_stream("pynba", "VERSION") as version_file:
        version = version_file.read().decode("utf-8").strip()
    return version


__version__ = __get_version()
