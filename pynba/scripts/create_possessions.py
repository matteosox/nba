"""Script to load possessions from pbpstats for all seasons on file, and store them"""

import logging

from pynba import (
    possessions_from_season,
    save_possessions,
    seasons_on_file,
    season_from_file,
)


logger = logging.getLogger(__name__)


def main():
    """Load possessions from pbpstats for all seasons on file, and store them"""
    season_info = seasons_on_file()
    for league, year, season_type in zip(
        season_info["league"], season_info["year"], season_info["season_type"]
    ):
        logger.info(f"Loading season data for {league} {year} {season_type} from file")
        season = season_from_file(league, year, season_type)
        logger.info(
            f"Parsing possessions data for {league} {year} {season_type} from pbpstats"
        )
        possessions = possessions_from_season(season)
        logger.info(f"Saving possessions data for {league} {year} {season_type}")
        save_possessions(possessions)
    logger.info("Complete")


if __name__ == "__main__":
    main()
