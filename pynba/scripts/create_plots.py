"""Script to save teams plots for all seasons on file"""

import logging

from pynba import seasons_on_file, save_stats_plot, teams_from_file


logger = logging.getLogger(__name__)


def main():
    """Generate and save plots for all seasons on file"""
    logger.info("Loading seasons on file")
    season_info = seasons_on_file()
    for league, year, season_type in zip(
        season_info["league"], season_info["year"], season_info["season_type"]
    ):
        logger.info(f"Loading teams data for {league} {year} {season_type} from file")
        teams = teams_from_file(league, year, season_type)
        logger.info("Creating & saving plots")
        save_stats_plot(teams)
    logger.info("Complete")


if __name__ == "__main__":
    main()
