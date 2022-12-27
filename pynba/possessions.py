"""Functions to manipulate possession data"""

import os
import logging

import pandas as pd
from pyarrow import BufferReader

from pynba.config import config
from pynba.parse_pbpstats_possessions import parse_possession
from pynba import load_pbpstats
from pynba.constants import LOCAL, S3
from pynba.aws_s3 import get_fileobject, NoSuchKey


__all__ = [
    "possessions_from_file",
    "possessions_from_game",
    "possessions_from_season",
    "save_possessions",
]

logger = logging.getLogger(__name__)


def _possessions_filename(league, year, season_type):
    return f"{league}_{year}_{season_type}_possessions.parquet"


def _possessions_filepath(league, year, season_type):
    filename = _possessions_filename(league, year, season_type)
    return os.path.join(
        config.local_data_directory, config.possessions_directory, filename
    )


def save_possessions(possessions):
    """
    Saves possessions data
    in the appropriate place and with proper partitioning
    """
    league = possessions["league"].iloc[0]
    year = possessions["year"].iloc[0]
    season_type = possessions["season_type"].iloc[0]
    possessions.to_parquet(_possessions_filepath(league, year, season_type))


def possessions_from_file(league, year, season_type):
    """
    Loads possessions data from file

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
    if config.possessions_source == LOCAL:
        filepath_or_buffer = pd.read_parquet(
            _possessions_filepath(league, year, season_type)
        )
    elif config.possessions_source == S3:
        filename = _possessions_filename(league, year, season_type)
        key = "/".join(
            [config.aws_s3_key_prefix, config.possessions_directory, filename]
        )
        try:
            fileobject = get_fileobject(config.aws_s3_bucket, key)
        except NoSuchKey as exc:
            raise FileNotFoundError(
                f"No such key {key} in bucket {config.aws_s3_bucket}"
            ) from exc
        filepath_or_buffer = BufferReader(fileobject.read())
    else:
        raise ValueError(
            f"Incompatible config for possessions source data: {config.seasons_source}"
        )
    return pd.read_parquet(filepath_or_buffer)


def possessions_from_game(game_data):
    """
    Loads possessions data from pbpstats

    Parameters
    ----------
    game_data : dict
        usually gotten from a row of a season

    Returns
    -------
    pd.DataFrame
    """
    game_id = game_data["game_id"]
    game = load_pbpstats.load_game(str(game_id))
    possessions_data = pd.DataFrame(
        parse_possession(possession) for possession in game.possessions.items
    )
    possessions_data["possession_num"] = possessions_data.index
    possessions_data["game_id"] = game_id
    possessions_data["date"] = game_data["date"]
    possessions_data["home_team_id"] = game_data["home_team_id"]
    possessions_data["away_team_id"] = game_data["away_team_id"]
    possessions_data["status"] = game_data["status"]
    possessions_data["league"] = game_data["league"]
    possessions_data["year"] = game_data["year"]
    possessions_data["season_type"] = game_data["season_type"]
    return possessions_data


def possessions_from_season(season):
    """
    Loads a season's worth of possessions data from pbpstats

    Parameters
    ----------
    season: pd.DataFrame
        each row representing a game

    Returns
    -------
    pd.DataFrame
    """
    raw_possessions = []
    for game_tuple in season.itertuples():
        game_data = game_tuple._asdict()
        try:
            raw_possessions.append(possessions_from_game(game_data))
        except load_pbpstats.StatsNotFound as exc:
            logger.info(exc.args[0])

    return pd.concat(
        raw_possessions,
        ignore_index=True,
    )
