"""Functions to manipulate season data"""

import os
import logging

import pandas as pd

from pynba.config import config
from pynba.constants import WNBA, LOCAL, S3
from pynba import load_pbpstats
from pynba.parquet import load_pq_to_df, save_df_to_pq
from pynba.aws_s3 import list_objects


__all__ = [
    "season_from_file",
    "season_from_pbpstats",
    "seasons_on_file",
    "save_season",
]

logger = logging.getLogger(__name__)


def save_season(season):
    """Save season data as a csv"""
    league = season["league"].iloc[0]
    year = season["year"].iloc[0]
    season_type = season["season_type"].iloc[0]

    save_df_to_pq(season, _season_filepath(league, year, season_type))


def _season_filename(league, year, season_type):
    return f"{league}_{year}_{season_type}_games.parquet"


def _seasons_dir():
    return os.path.join(config.local_data_directory, config.seasons_directory)


def _season_filepath(league, year, season_type):
    return os.path.join(_seasons_dir(), _season_filename(league, year, season_type))


def seasons_on_file():
    """Produces a Pandas DataFrame with info on the seasons on file"""
    if config.seasons_source == LOCAL:
        filenames = os.listdir(_seasons_dir())
    elif config.seasons_source == S3:
        prefix = f"{config.aws_s3_key_prefix}/{config.seasons_directory}/"
        objects = list_objects(config.aws_s3_bucket, Prefix=prefix)
        filenames = [obj["Key"][len(prefix) :] for obj in objects]
    else:
        raise ValueError(
            f"Incompatible config for season source data: {config.seasons_source}"
        )

    leagues, years, season_types = zip(
        *[fn.split(".")[0].split("_")[:3] for fn in filenames]
    )
    return pd.DataFrame(
        {
            "league": leagues,
            "year": [int(year) for year in years],
            "season_type": season_types,
        }
    ).sort_values(by=["league", "year", "season_type"], ascending=False)


def season_from_file(league, year, season_type):
    """
    Loads season data from file

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
    if config.seasons_source == LOCAL:
        source = _season_filepath(league, year, season_type)
    elif config.seasons_source == S3:
        filename = _season_filename(league, year, season_type)
        source = (
            f"s3://{config.aws_s3_bucket}/{config.aws_s3_key_prefix}/"
            f"{config.seasons_directory}/{filename}"
        )
    else:
        raise ValueError(
            f"Incompatible config for season source data: {config.seasons_source}"
        )
    return load_pq_to_df(source)


def season_from_pbpstats(league, year, season_type):
    """
    Loads season data from pbpstats data

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
    pbpstats_year = _parse_year(year, league)
    pbpstats_season = load_pbpstats.load_season_from_web(
        league, pbpstats_year, season_type
    )
    season = pd.DataFrame(pbpstats_season.games.final_games)
    season["league"] = league
    season["year"] = year
    season["season_type"] = season_type
    if "visitor_team_id" in season:
        season.rename(
            columns={"visitor_team_id": "away_team_id"}, copy=False, inplace=True
        )
    return season


def _parse_year(year, league):
    """
    Parses a year integer into a pbpstats
    compatible year string. The year int represents
    the end of the season.
    """
    if league == WNBA:
        return str(year)
    return f"{year - 1}-{(year) % 100:02}"
