"""Module for loading NBA team information"""

from pkg_resources import resource_filename

from pynba import safe_yaml


__all__ = ["team_id_to_abb"]
DATA_PATH = resource_filename("pynba", "teams.yaml")

with open(DATA_PATH) as teams_yaml:
    team_info = safe_yaml.load(teams_yaml)


def team_id_to_abb(league, year):
    """Returns a dictionary mapping a team_id to its abbreviation for that league/year"""
    return {key: val["abbreviation"] for key, val in team_info[league][year].items()}
