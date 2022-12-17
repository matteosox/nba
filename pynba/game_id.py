"""Module for parsing game_ids to get relevant information"""

from pynba.constants import NBA, WNBA

GAME_ID_PREFIXES = {
    "00": NBA,
    "10": WNBA,
}
SEASON_TYPE_STRS = {
    "2": "Regular Season",
    "4": "Playoffs",
    "5": "Play In",
}
STATS_YEAR_CUTOFF = 80


def league_from_game_id(game_id):
    """Derive the league string from the game_id string"""
    try:
        return GAME_ID_PREFIXES[game_id[:2]]
    except KeyError as exc:
        raise ValueError(f"game_id {game_id} has unrecognized prefix") from exc


def year_from_game_id(game_id):
    """Derive the year int from the game_id string"""
    league = league_from_game_id(game_id)
    digits = int(game_id[3:5])
    century = 2000 if digits < STATS_YEAR_CUTOFF else 1900
    return century + digits + (league != WNBA)


def season_type_from_game_id(game_id):
    """Derive the season_type string from the game_id string"""
    try:
        return SEASON_TYPE_STRS[game_id[2]]
    except KeyError as exc:
        raise ValueError(f"game_id {game_id} has unrecognized third digit") from exc
