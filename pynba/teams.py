"""Functions to manipulate teams data"""

import os
import logging

import pandas as pd

from pynba.config import config
from pynba.team_stats import TeamsModel
from pynba.constants import LOCAL, S3
from pynba.aws_s3 import get_fileobject


__all__ = [
    "save_teams",
    "teams_from_file",
    "teams_from_halfgames",
]

logger = logging.getLogger(__name__)


def save_teams(teams):
    """Saves teams data as a csv in the appropriate place"""
    league = teams["league"].iloc[0]
    year = teams["year"].iloc[0]
    season_type = teams["season_type"].iloc[0]

    os.makedirs(_teams_dir(), exist_ok=True)
    teams.to_csv(_teams_filepath(league, year, season_type), index=False)


def _teams_filename(league, year, season_type):
    return f"{league}_{year}_{season_type}_teams.csv"


def _teams_filepath(league, year, season_type):
    return os.path.join(
        _teams_dir(),
        _teams_filename(league, year, season_type),
    )


def _teams_dir():
    return os.path.join(config.local_data_directory, config.teams_directory)


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
    if config.teams_source == LOCAL:
        filepath_or_buffer = _teams_filepath(league, year, season_type)
    elif config.teams_source == S3:
        filename = _teams_filename(league, year, season_type)
        key = "/".join([config.aws_s3_key_prefix, config.teams_directory, filename])
        filepath_or_buffer = get_fileobject(config.aws_s3_bucket, key)
    else:
        raise ValueError(
            f"Incompatible config for teams source data: {config.teams_source}"
        )
    return pd.read_csv(filepath_or_buffer)


def teams_from_halfgames(halfgames):
    """Calculates teams data from halfgames data"""
    logger.info("Building model")
    teams_model = TeamsModel(halfgames)
    logger.info("Fitting model")
    teams_model.fit()
    return teams_model.results
