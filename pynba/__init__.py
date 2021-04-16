"""Hodge podge of NBA stats and analysis utilities"""

from pkg_resources import resource_stream as __resource_stream

from pynba import logging as __logging
from pynba.team_info import *
from pynba.seasons import (
    season_from_file,
    season_from_pbpstats,
    seasons_on_file,
    save_season,
)
from pynba.possessions import (
    possessions_from_file,
    possessions_from_season,
    save_possessions,
)
from pynba.halfgames import halfgames_from_file, halfgames_from_possessions
from pynba.teams import save_teams, teams_from_file, teams_from_halfgames
from pynba.plot import plot_logos, plot_paces, plot_ratings, use_blackontrans_style


def __get_version():
    with __resource_stream("pynba", "VERSION") as version_file:
        version = version_file.read().decode("utf-8").strip()
    return version


__version__ = __get_version()
