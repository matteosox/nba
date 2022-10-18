"""Script to calculate and save teams data for all seasons on file"""

import logging

from pynba import (
    seasons_on_file,
    halfgames_from_file,
    teams_from_halfgames,
    save_teams,
    save_team_plots,
)


logger = logging.getLogger(__name__)


def main():
    """Calculate and save teams data for all seasons on file"""
    logger.info("Loading seasons on file")
    season_info = seasons_on_file()
    for league, year, season_type in zip(
        season_info["league"], season_info["year"], season_info["season_type"]
    ):
        logger.info(
            f"Loading halfgame data for {league} {year} {season_type} from file"
        )
        halfgames = halfgames_from_file(league, year, season_type)
        logger.info(
            f"Calculating team statistics for {league} {year} {season_type} from halfgames"
        )
        teams = teams_from_halfgames(halfgames)
        logger.info(f"Saving teams data for {league} {year} {season_type}")
        save_teams(teams)
        logger.info("Plotting & saving team ratings & pace")
        save_team_plots(teams)
    logger.info("Complete")


if __name__ == "__main__":
    main()
