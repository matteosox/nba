"""Script to calculate and save teams data for all seasons on file"""

import logging
import os

from matplotlib import pyplot as plt

from pynba import (
    seasons_on_file,
    halfgames_from_file,
    teams_from_halfgames,
    save_teams,
    plot_ratings,
    plot_paces,
    use_blackontrans_style,
)
from pynba.config import Config


logger = logging.getLogger(__name__)

use_blackontrans_style()


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
        plot_stuff(teams)
    logger.info("Complete")


def plot_stuff(teams):
    """
    Plot stuff from the teams data (to be replaced by D3 interactives)
    """
    league = teams["league"].iloc[0]
    year = teams["year"].iloc[0]
    season_type = teams["season_type"].iloc[0]

    fig = plt.figure(figsize=(8, 8))
    axis = fig.add_subplot(1, 1, 1)
    plot_ratings(teams, axis)
    fig.savefig(
        os.path.join(
            Config.local_data_directory,
            Config.plots_directory,
            f"team_ratings_{league}_{year}_{season_type}.png",
        )
    )

    fig = plt.figure(figsize=(8, 8))
    axis = fig.add_subplot(1, 1, 1)
    plot_paces(teams, axis)
    fig.savefig(
        os.path.join(
            Config.local_data_directory,
            Config.plots_directory,
            f"team_paces_{league}_{year}_{season_type}.png",
        )
    )


if __name__ == "__main__":
    main()
