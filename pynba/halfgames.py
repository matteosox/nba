"""Module of functions to load and manipulate halfgames and their stats"""

from pynba.possessions import possessions_from_file


__all__ = [
    "halfgames_from_file",
    "halfgames_from_possessions",
]


def halfgames_from_file(league, year, season_type):
    """Load NBA halfgame data

    Parameters
    ----------
    ...

    Returns
    -------
    Pandas DataFrame where each row is a halfgame
    """
    possessions = possessions_from_file(league, year, season_type)
    return halfgames_from_possessions(possessions)


def halfgames_from_possessions(possessions):
    """
    Processes a Pandas DataFrame of possessions data
    into a Pandas DataFrame of games, where each game has an
    entry for home-offense and visitor-offense.
    """
    # aggregate possessions per game & offense
    halfgames = possessions.groupby(by=["game_id", "off_team_id"], as_index=False).agg(
        {
            "def_team_id": "first",
            "home_team_id": "first",
            "league": "first",
            "year": "first",
            "season_type": "first",
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
    halfgames["three_make_rate"] = (
        halfgames["threes_made"] / halfgames["threes_attempted"]
    )
    halfgames["two_make_rate"] = halfgames["twos_made"] / halfgames["twos_attempted"]
    halfgames["three_attempt_rate"] = halfgames["threes_attempted"] / (
        halfgames["twos_attempted"] + halfgames["threes_attempted"]
    )
    halfgames["ft_attempt_rate"] = (
        halfgames["ft_attempted"] / halfgames["possession_num"]
    )
    halfgames["ft_make_rate"] = halfgames["ft_made"] / halfgames["ft_attempted"]
    halfgames["off_reb_rate"] = halfgames["off_rebs"] / (
        halfgames["off_rebs"] + halfgames["def_rebs"]
    )
    halfgames["turnover_rate"] = halfgames["turnovers"] / halfgames["possession_num"]
    halfgames["pace"] = halfgames["duration"] / halfgames["possession_num"]
    halfgames["shots_per_opp"] = (
        halfgames["threes_attempted"] + halfgames["twos_attempted"]
    ) / (halfgames["off_rebs"] + halfgames["possession_num"])
    halfgames["shots_per_poss"] = (
        halfgames["twos_attempted"] + halfgames["threes_attempted"]
    ) / halfgames["possession_num"]
    halfgames["scoring_rate"] = halfgames["points_scored"] / halfgames["possession_num"]

    # estimate scoring rate based on underlying rate statistics
    halfgames["shots_per_opp_est"] = estimate_shots_per_opp(
        halfgames["turnover_rate"],
        halfgames["ft_attempt_rate"],
    )
    halfgames["shots_per_poss_est"] = estimate_shots_per_poss(
        halfgames["shots_per_opp_est"],
        halfgames["three_attempt_rate"],
        halfgames["three_make_rate"],
        halfgames["two_make_rate"],
        halfgames["off_reb_rate"],
    )
    halfgames["scoring_rate_est"] = calc_scoring_rate(
        halfgames["shots_per_poss_est"],
        halfgames["three_make_rate"],
        halfgames["two_make_rate"],
        halfgames["three_attempt_rate"],
        halfgames["ft_attempt_rate"],
        halfgames["ft_make_rate"],
    )

    return halfgames


def estimate_shots_per_opp(turnover_rate, ft_attempt_rate):
    """
    Estimates shot attempts per potential shot opportunity, i.e.
    possessions plus offensive rebounds. Coefficients are rounded
    from a simple least-squared regression from regular-season data.
    """
    return 1 - 0.85 * turnover_rate - 0.4 * ft_attempt_rate


def estimate_shots_per_poss(
    shots_per_opp, three_attempt_rate, three_make_rate, two_make_rate, off_reb_rate
):
    """
    Estimates shot attempts per possession given shot attempts per opportunity,
    (see above for definition), then taking into account how frequently shots are missed
    and rebounded by the offense.
    """
    no_shots_per_opp = 1 - shots_per_opp
    make_rate = (
        three_attempt_rate * three_make_rate + (1 - three_attempt_rate) * two_make_rate
    )
    miss_rate = 1 - make_rate
    def_reb_rate = 1 - off_reb_rate

    restart_possession = shots_per_opp * miss_rate * off_reb_rate
    last_shot = shots_per_opp * (
        make_rate + miss_rate * (def_reb_rate + off_reb_rate * no_shots_per_opp)
    )
    return last_shot / (1 - restart_possession) ** 2


def calc_scoring_rate(
    shots_per_poss,
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
    return shots_per_poss * points_per_attempt + ft_attempt_rate * ft_make_rate
