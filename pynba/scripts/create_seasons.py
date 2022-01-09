"""Script to query and store seasons data from scratch"""

import logging
import datetime

from pynba import season_from_pbpstats, save_season
from pynba.constants import NBA, WNBA, SEASON_TYPES
from pynba.load_pbpstats import StatsNotFound


logger = logging.getLogger(__name__)

CURRENT_YEAR = datetime.datetime.now().year
LEAGUE_YEARS = {
    NBA: range(2001, CURRENT_YEAR + 2),
    WNBA: range(2009, CURRENT_YEAR + 1),
}
LEAGUE_YEAR_SEASON_TYPES = [
    (league, year, season_type)
    for league, years in LEAGUE_YEARS.items()
    for year in years
    for season_type in SEASON_TYPES
]


def main():
    """Query and store seasons data from scratch"""
    for league, year, season_type in LEAGUE_YEAR_SEASON_TYPES:
        logger.info(
            f"Loading season data for {league} {year} {season_type} from pbpstats"
        )
        try:
            season = season_from_pbpstats(league, year, season_type)
        except StatsNotFound as exc:
            logger.info(exc.args[0])
            continue
        logger.info(f"Saving season data for {league} {year} {season_type}")
        save_season(season)
    logger.info("Complete")


if __name__ == "__main__":
    main()
