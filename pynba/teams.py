"""Functions to manipulate teams data"""

import os
import logging

import pandas as pd

from pynba.config import Config
from pynba.team_stats import TeamsModel


logger = logging.getLogger(__name__)

TEAMS_DIR = os.path.join(Config.local_data_directory, Config.teams_directory)


def save_teams(teams):
    """Saves teams data as a csv in the appropriate place"""
    league = teams["league"].iloc[0]
    year = teams["year"].iloc[0]
    season_type = teams["season_type"].iloc[0]
    teams.to_csv(_teams_filepath(league, year, season_type), index=False)


def _teams_filepath(league, year, season_type):
    return os.path.join(TEAMS_DIR, f"{league}_{year}_{season_type}_teams.csv")


def teams_from_file(league, year, season_type):
    """
    Loads teams data from file

    Parameters
    ----------
    league : str
        e.g. "nba", "wnba"
    year : int
        e.g. 2018
    season_type : str
        e.g. "Regular Season", "Playoffs"

    Returns
    -------
    pd.DataFrame
    """
    filepath = _teams_filepath(league, year, season_type)
    return pd.read_csv(filepath)


def teams_from_halfgames(halfgames):
    """Calculates teams data from halfgames data"""
    logger.info("Building model")
    teams_model = TeamsModel(halfgames)
    logger.info("Fitting model")
    teams_model.fit()
    return teams_model.results
