"""Functions to manipulate possession data"""

import os
import logging

import pandas as pd
import pyarrow
from pyarrow import parquet

from pynba.config import Config
from pynba.parse_pbpstats_possessions import parse_possession
from pynba import load_pbpstats


logger = logging.getLogger(__name__)

POSSESSIONS_DIR = os.path.join(
    Config.local_data_directory, Config.possessions_directory
)
MULTIYEAR_LEAGUES = {"nba", "gleague"}


def _load_pq_to_df(path, *args, **kwargs):
    """Function to load Parquet into Pandas"""
    return parquet.read_table(path, *args, **kwargs).to_pandas()


def _save_df_to_pq(dataframe, path, *args, **kwargs):
    """Function to save Pandas into Parquet"""
    table = pyarrow.Table.from_pandas(dataframe, preserve_index=False)
    parquet.write_to_dataset(table, path, *args, **kwargs)


def save_possessions(possessions):
    """
    Saves possessions data
    in the appropriate place and with proper partitioning
    """
    _save_df_to_pq(
        possessions, POSSESSIONS_DIR, partition_cols=["league", "year", "season_type"]
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
    filters = [
        [
            ("league", "=", league),
            ("year", "=", year),
            ("season_type", "=", season_type),
        ]
        for season_type in season_type.split("+")
    ]
    return _load_pq_to_df(POSSESSIONS_DIR, filters=filters)


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
