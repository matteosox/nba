"""Functions to parse pbpstats data"""

from pbpstats.resources.enhanced_pbp import FieldGoal, FreeThrow, Rebound, Turnover


def parse_possession(possession):
    """
    Parse a possession's worth of pbpstats data

    Parameters
    ----------
    possession : pbpstats game.possessions.items

    Returns
    -------
    dict
    """
    off_team_id = possession.offense_team_id
    current_players = possession.events[0].current_players
    def_team_id = [a for a in current_players if a != off_team_id][0]
    row = {
        "off_team_id": off_team_id,
        "def_team_id": def_team_id,
        "period": possession.period,
        "start_time": clock_to_seconds_remaining(possession.start_time),
        "end_time": clock_to_seconds_remaining(possession.end_time),
        "start_score_margin": possession.start_score_margin,
    }
    row["duration"] = row["start_time"] - row["end_time"]
    row.update(
        {
            f"off_player{ind}": player_id
            for ind, player_id in enumerate(current_players[off_team_id])
        }
    )
    row.update(
        {
            f"def_player{ind}": player_id
            for ind, player_id in enumerate(current_players[def_team_id])
        }
    )
    row.update(parse_events(possession.events))
    return row


def parse_events(events):
    """
    Parse the events associated with a pbpstats possession

    Parameters
    ----------
    events : pbpstats possession.events

    Returns
    -------
    dict
    """
    subrow = {
        "threes_attempted": 0,
        "threes_made": 0,
        "twos_attempted": 0,
        "twos_made": 0,
        "ft_attempted": 0,
        "ft_made": 0,
        "off_rebs": 0,
        "def_rebs": 0,
        "turnovers": 0,
        "points_scored": 0,
    }
    for event in events:
        if isinstance(event, FieldGoal):
            _process_fg(event, subrow)
        elif isinstance(event, FreeThrow):
            _process_ft(event, subrow)
        elif isinstance(event, Rebound):
            _process_reb(event, subrow)
        elif isinstance(event, Turnover):
            _process_to(event, subrow)
    return subrow


def _process_fg(event, subrow):
    if event.shot_value == 2:
        subrow["twos_attempted"] += 1
        if event.is_made:
            subrow["twos_made"] += 1
            subrow["points_scored"] += 2
    else:
        subrow["threes_attempted"] += 1
        if event.is_made:
            subrow["threes_made"] += 1
            subrow["points_scored"] += 3


def _process_ft(event, subrow):
    if not event.is_technical_ft:
        subrow["ft_attempted"] += 1
        if event.is_made:
            subrow["ft_made"] += 1
            subrow["points_scored"] += event.shot_value


def _process_reb(event, subrow):
    if event.is_real_rebound:
        if event.oreb:
            subrow["off_rebs"] += 1
        else:
            subrow["def_rebs"] += 1


def _process_to(event, subrow):
    if not event.is_no_turnover:
        subrow["turnovers"] += 1


def clock_to_seconds_remaining(clock_str):
    """Translates a clock string to a number of seconds remaining"""
    minutes, seconds = clock_str.split(":")
    return float(minutes) * 60 + float(seconds)
