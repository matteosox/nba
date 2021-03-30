"""Load parsed nba data"""

from pyarrow import parquet


def _load_parquet(path, filters, *args, **kwargs):
    """Simple function to load Parquet into Pandas"""
    return parquet.read_table(path, *args, filters=filters, **kwargs).to_pandas()


def load_games(path, filters):
    """Load NBA game data

    Parameters
    ----------
    path : str
        path to Parquet directory of parsed pbpstats possession data
    filters : list
        list of list of tuples, e.g. [[("thing", "=", 3)]]
        see https://arrow.apache.org/docs/python/generated/pyarrow.parquet.read_table.html

    Returns
    -------
    Pandas DataFrame
    """
    possessions = _load_parquet(path, filters)
    return process_possessions(possessions)


def process_possessions(possessions):
    """
    Processes a Pandas DataFrame of pbpstats parsed possessions
    into a Pandas DataFrame of games, where each game has an
    entry for home-offense and visitor-offense.
    """
    # aggregate possessions per game & offense
    games = possessions.groupby(by=["game_id", "off_team_id"], as_index=False).agg(
        {
            "def_team_id": "first",
            "home_team_id": "first",
            "year": "first",
            "date": "first",
            "turnovers": "sum",
            "threes_attempted": "sum",
            "threes_made": "sum",
            "twos_attempted": "sum",
            "twos_made": "sum",
            "ft_attempted": "sum",
            "ft_made": "sum",
            "off_rebs": "sum",
            "def_rebs": "sum",
            "points_scored": "sum",
            "duration": "sum",
            "possession_num": "count",
            "period": "max",
        }
    )

    # calculate rate statistics
    games["three_make_rate"] = games["threes_made"] / games["threes_attempted"]
    games["two_make_rate"] = games["twos_made"] / games["twos_attempted"]
    games["three_attempt_rate"] = games["threes_attempted"] / (
        games["twos_attempted"] + games["threes_attempted"]
    )
    games["ft_attempt_rate"] = games["ft_attempted"] / games["possession_num"]
    games["ft_make_rate"] = games["ft_made"] / games["ft_attempted"]
    games["off_reb_rate"] = games["off_rebs"] / (games["off_rebs"] + games["def_rebs"])
    games["turnover_rate"] = games["turnovers"] / games["possession_num"]
    games["pace"] = games["duration"] / games["possession_num"]
    games["shot_rate"] = (games["threes_attempted"] + games["twos_attempted"]) / (
        games["off_rebs"] + games["possession_num"]
    )
    games["attempt_rate"] = (
        games["twos_attempted"] + games["threes_attempted"]
    ) / games["possession_num"]
    games["scoring_rate"] = games["points_scored"] / games["possession_num"]

    # estimate scoring rate based on underlying rate statistics
    games["shot_rate_est"] = estimate_shot_rate(
        games["turnover_rate"],
        games["ft_attempt_rate"],
    )
    games["attempt_rate_est"] = estimate_attempt_rate(
        games["shot_rate_est"],
        games["three_attempt_rate"],
        games["three_make_rate"],
        games["two_make_rate"],
        games["off_reb_rate"],
    )
    games["scoring_rate_est"] = calc_scoring_rate(
        games["attempt_rate_est"],
        games["three_make_rate"],
        games["two_make_rate"],
        games["three_attempt_rate"],
        games["ft_attempt_rate"],
        games["ft_make_rate"],
    )

    return games


def estimate_shot_rate(turnover_rate, ft_attempt_rate):
    """
    Estimates shot_rate: shot attempts per potential shot attempt event, i.e.
    possessions plus offensive rebounds. Coefficients are rounded
    from a simple least-squared regression from regular-season data.
    """
    return 1 - 0.85 * turnover_rate - 0.4 * ft_attempt_rate


def estimate_attempt_rate(
    shot_rate, three_attempt_rate, three_make_rate, two_make_rate, off_reb_rate
):
    """
    Estimates attempt_rate (shot attempts per possession) given a shot_rate
    (see above for definition), then taking into account how frequently shots are missed
    and rebounded by the offense.
    """
    no_shot_rate = 1 - shot_rate
    make_rate = (
        three_attempt_rate * three_make_rate + (1 - three_attempt_rate) * two_make_rate
    )
    miss_rate = 1 - make_rate
    def_reb_rate = 1 - off_reb_rate

    restart_possession = shot_rate * miss_rate * off_reb_rate
    last_shot = shot_rate * (
        make_rate + miss_rate * (def_reb_rate + off_reb_rate * no_shot_rate)
    )
    return last_shot / (1 - restart_possession) ** 2


def calc_scoring_rate(
    attempt_rate,
    three_make_rate,
    two_make_rate,
    three_attempt_rate,
    ft_attempt_rate,
    ft_make_rate,
):
    """Calculates points per possession from underlying rate statistics"""
    points_per_attempt = (
        3 * three_attempt_rate * three_make_rate
        + 2 * (1 - three_attempt_rate) * two_make_rate
    )
    return attempt_rate * points_per_attempt + ft_attempt_rate * ft_make_rate
