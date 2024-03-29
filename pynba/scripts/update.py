"""Script to update nba data"""

import logging
import os
import datetime
import time

import pandas as pd

from pynba import (
    season_from_file,
    season_from_pbpstats,
    save_season,
    possessions_from_file,
    possessions_from_season,
    save_possessions,
    halfgames_from_possessions,
    teams_from_halfgames,
    save_teams,
    save_stats_plot,
)
from pynba.config import config
from pynba.constants import NBA, WNBA, MULTIYEAR_LEAGUES, SEASON_TYPES
from pynba import safe_yaml
from pynba.load_pbpstats import StatsNotFound


logger = logging.getLogger(__name__)


def update_season(league, year, season_type):
    """
    Updates the season for the given inputs:
        1) Loads updated season data from pbpstats.
        2) Loads season data from file.
        3) If there are no missing games, quits.
        4) Saves updated season data to file.
        5) Loads possession data for the missing games from pbpstats.
        6) Loads possessions data from earlier games from file.
        7) Saves the combined possession data to file.
        8) Calculates halfgame data from the possessions.
        9) Calculates team data from the joined halfgame data.
        10) Saves updated team data to file.
        11) Saves updated team plots to file.
    """
    logger.info(
        f"Loading season data for the {league} {year} {season_type} from pbpstats"
    )
    try:
        updated_season = season_from_pbpstats(league, year, season_type)
    except StatsNotFound:
        logger.info(
            f"No stats found for the {league} {year} {season_type}, so no update required"
        )
        return

    logger.info(f"Loading season data for the {league} {year} {season_type} from file")
    try:
        season = season_from_file(league, year, season_type)
    except FileNotFoundError:
        missing_games = set(updated_season["game_id"])
    else:
        missing_games = set(updated_season["game_id"]) - set(season["game_id"])
    if not missing_games:
        logger.info(
            "No games missing from season data on file "
            f"for the {league} {year} {season_type}, so no update required"
        )
        return

    logger.info(f"Saving updated season data for the {league} {year} {season_type}")
    save_season(updated_season)

    logger.info(
        f"Loading possessions data for {len(missing_games)} missing games "
        f"for the {league} {year} {season_type} from pbpstats"
    )
    filt = updated_season["game_id"].map(lambda game_id: game_id in missing_games)
    missing_season = updated_season[filt]
    missing_possessions = possessions_from_season(missing_season)

    try:
        earlier_possessions = possessions_from_file(league, year, season_type)
    except FileNotFoundError:
        if missing_games != set(updated_season["game_id"]):
            raise
        logger.info(
            f"No possessions data for the {league} {year} {season_type} found from file, "
            "but this is alright since saved season contained no games."
        )
        updated_possessions = missing_possessions
    else:
        updated_possessions = pd.concat(
            [earlier_possessions, missing_possessions], ignore_index=True
        )

    logger.info(f"Saving possessions data for the {league} {year} {season_type}")
    save_possessions(updated_possessions)

    logger.info("Calculating halfgames data " f"for the {league} {year} {season_type}")
    halfgames = halfgames_from_possessions(updated_possessions)

    logger.info(
        "Calculating team statistics "
        f"for the {league} {year} {season_type} from updated halfgames"
    )
    teams = teams_from_halfgames(halfgames)

    logger.info(f"Saving teams data for the {league} {year} {season_type}")
    save_teams(teams)

    logger.info(
        f"Plotting & saving team ratings & pace for the {league} {year} {season_type}"
    )
    save_stats_plot(teams)

    logger.info(f"Finished updating data for the {league} {year} {season_type}")


def write_latest():
    """Writes a small file with information on data provenance"""
    filepath = os.path.join(config.local_data_directory, "latest.yaml")
    data = {"git_sha": config.git_sha, "time": time.time()}
    with open(filepath, "w", encoding="utf-8") as latest_file:
        safe_yaml.dump(data, latest_file)


def main():
    """
    Update data on file for all leagues and season types
    for the current year and next one for multi-year leagues
    """
    current_year = datetime.datetime.now().year
    logger.info(f"Determine current year as {current_year}")
    for league in [NBA, WNBA]:
        years = [current_year]
        if league in MULTIYEAR_LEAGUES:
            years = [current_year, current_year + 1]
        for year in years:
            for season_type in SEASON_TYPES:
                logger.info(f"Updating stats for season {league} {year} {season_type}")
                update_season(league, year, season_type)
    logger.info("Writing latest.yaml file")
    write_latest()
    logger.info("Complete!")


if __name__ == "__main__":
    main()
