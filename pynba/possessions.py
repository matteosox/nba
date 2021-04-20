"""Functions to manipulate possession data"""

import os
import logging

import pandas as pd

from pynba.config import config
from pynba.parse_pbpstats_possessions import parse_possession
from pynba import load_pbpstats
from pynba.parquet import load_pq_to_df, save_df_to_pq
from pynba.constants import LOCAL, S3


__all__ = [
    "possessions_from_file",
    "possessions_from_season",
    "save_possessions",
]

logger = logging.getLogger(__name__)


def _possessions_dir():
    return os.path.join(config.local_data_directory, config.possessions_directory)


def save_possessions(possessions):
    """
    Saves possessions data
    in the appropriate place and with proper partitioning
    """
    os.makedirs(_possessions_dir(), exist_ok=True)
    save_df_to_pq(
        possessions,
        _possessions_dir(),
        partition_cols=["league", "year", "season_type"],
    )


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
        source = _possessions_dir()
        filters = [
            [
                ("league", "=", league),
                ("year", "=", year),
                ("season_type", "=", season_type),
            ]
            for season_type in season_type.split("+")
        ]
        return load_pq_to_df(source, filters=filters)
    if config.possessions_source == S3:
        source = (
            f"s3://{config.aws_s3_bucket}/{config.aws_s3_key_prefix}/"
            f"{config.possessions_directory}"
        )
        partition_filter = (
            lambda x: (x["league"] == league)
            & (x["year"] == str(year))
            & (x["season_type"] == season_type)
        )
        possessions = load_pq_to_df(
            source, dataset=True, partition_filter=partition_filter
        )
        # awswrangler doesn't download partitions, uses strings for their types
        possessions["year"] = possessions["year"].astype(int)
        return possessions

    raise ValueError(
        f"Incompatible config for possessions source data: {config.possessions_source}"
    )


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
