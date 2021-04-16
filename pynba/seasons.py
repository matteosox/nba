"""Functions to manipulate season data"""

import os
import logging

import pandas as pd

from pynba.config import Config
from pynba import load_pbpstats


logger = logging.getLogger(__name__)

SEASONS_DIR = os.path.join(Config.local_data_directory, Config.seasons_directory)
WNBA = "wnba"


def save_season(season):
    """Save season data as a csv"""
    league = season["league"].iloc[0]
    year = season["year"].iloc[0]
    season_type = season["season_type"].iloc[0]
    season.to_parquet(_season_filepath(league, year, season_type), index=False)


def _season_filepath(league, year, season_type):
    return os.path.join(SEASONS_DIR, f"{league}_{year}_{season_type}_games.parquet")


def seasons_on_file():
    """Produces a Pandas DataFrame with info on the seasons on file"""
    filenames = os.listdir(SEASONS_DIR)
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
    filepath = _season_filepath(league, year, season_type)
    return pd.read_parquet(filepath)


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
