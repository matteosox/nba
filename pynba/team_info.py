"""Module for loading NBA team information"""

from pkg_resources import resource_filename

from pynba import safe_yaml


__all__ = ["team_id_to_abb"]


def __load_team_info():
    team_info_path = resource_filename("pynba", "teams.yaml")
    with open(team_info_path, encoding="utf-8") as teams_file:
        return safe_yaml.load(teams_file)


def team_id_to_abb(league, year):
    """Returns a dictionary mapping a team's id to its abbreviation for that league/year"""
    return {key: val["abbreviation"] for key, val in team_info[league][year].items()}


def team_abb_to_id(league, year):
    """Returns a dictionary mapping a team's abbreviation to its id for that league/year"""
    return {val["abbreviation"]: key for key, val in team_info[league][year].items()}


team_info = __load_team_info()
