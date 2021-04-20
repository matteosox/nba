"""Module of functions to load pbpstats data"""

import logging

from requests import ReadTimeout, HTTPError

from pynba.pbpstats_client import pbpstats_client
from pynba.game_id import league_from_game_id, year_from_game_id
from pynba.constants import NBA, WNBA, G_LEAGUE, FILE, WEB, STATS_NBA, DATA_NBA


logger = logging.getLogger(__name__)

LEAGUE_SEASON_PROVIDERS = {
    NBA: STATS_NBA,
    WNBA: DATA_NBA,
    G_LEAGUE: DATA_NBA,
}
STATS_NBA_CUTOFF_YEAR = 2020
PBPSTATS_SUBDIRS = ["game_details", "overrides", "pbp", "schedule"]


class StatsNotFound(Exception):
    """Custom exception to raise when stats are unavailable"""


def load_season(league, year, season_type):
    """
    Loads pbpstats season object from file, falling back to web

    Parameters
    ----------
    league : str
        e.g. "nba", "wnba"
    year : str
        e.g. "2018", "2018-19"
    season_type : str
        e.g. "Regular Season", "Playoffs"

    Returns
    -------
    pbpstats Season object
    """
    client = pbpstats_client(FILE, LEAGUE_SEASON_PROVIDERS[league])
    try:
        season = client.Season(league, year, season_type)  # pylint: disable=no-member
    except Exception as exc:  # pylint: disable=broad-except
        msg = exc.args[0]
        if not msg.endswith(".json does not exist"):
            raise exc
        logger.info(
            f"{league} {year} {season_type} not found locally, so downloading it."
        )
    else:
        if season.games.final_games:
            return season
        logger.info(
            f"{league} {year} {season_type} is empty locally, so downloading it."
        )

    return load_season_from_web(league, year, season_type)


def load_season_from_web(league, year, season_type):
    """
    Loads pbpstats season object from the web

    Parameters
    ----------
    league : str
        e.g. "nba", "wnba"
    year : str
        e.g. "2018", "2018-19"
    season_type : str
        e.g. "Regular Season", "Playoffs"

    Returns
    -------
    pbpstats Season object
    """
    client = pbpstats_client(WEB, LEAGUE_SEASON_PROVIDERS[league])
    while True:
        try:
            season = client.Season(  # pylint: disable=no-member
                league, year, season_type
            )
        except HTTPError as exc:
            if exc.response.status_code == 404:
                raise StatsNotFound(
                    f"Didn't find data for {league} {year} {season_type}"
                ) from exc
            raise exc
        except ReadTimeout:
            logger.debug(f"Re-requesting data for {league} {year} {season_type}.")
        else:
            break

    if not season.games.final_games:
        raise StatsNotFound(f"Didn't find data for {league} {year} {season_type}")

    return season


def load_game(game_id):
    """
    Loads a pbpstats Game object from file, falling back to web

    Parameters
    ----------
    game_id : str

    Returns
    -------
    pbpstats Game object
    """
    stats_provider = _game_stats_provider(game_id)
    client = pbpstats_client(FILE, stats_provider)
    try:
        game = client.Game(game_id)  # pylint: disable=no-member
    except Exception as exc:  # pylint: disable=broad-except
        msg = exc.args[0]
        if not msg.endswith(".json does not exist"):
            raise exc
        logger.info(f"Game with id {game_id} not found locally, so downloading it.")
    else:
        if game.possessions.items:
            return game
        logger.info(f"Game with id {game_id} is empty locally, so downloading it.")

    return load_game_from_web(game_id)


def load_game_from_web(game_id):
    """
    Loads a pbpstats Game object from the web

    Parameters
    ----------
    game_id : str

    Returns
    -------
    pbpstats Game object
    """
    stats_provider = _game_stats_provider(game_id)
    client = pbpstats_client(WEB, stats_provider)
    while True:
        try:
            game = client.Game(game_id)  # pylint: disable=no-member
        except HTTPError as exc:
            if exc.response.status_code == 404:
                raise StatsNotFound(
                    f"Didn't find data for game with id {game_id}"
                ) from exc
            raise exc
        except ReadTimeout:
            logger.debug(f"Re-requesting data for game with id {game_id}.")
        else:
            break

    if not game.possessions.items:
        raise StatsNotFound(f"Game with id {game_id} contains no data.")

    return game


def _game_stats_provider(game_id):
    year = year_from_game_id(game_id)
    if year > STATS_NBA_CUTOFF_YEAR:
        league = league_from_game_id(game_id)
        if league == NBA:
            return DATA_NBA
    return STATS_NBA
