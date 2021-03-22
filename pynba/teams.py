"""Module for loading NBA team information"""

from pkg_resources import resource_filename

import pandas as pd


DATA_PATH = resource_filename("pynba", "teams.json")

team_info = pd.read_json(DATA_PATH)
team_id_to_team_abb = {row.team_id: row.abbreviation for row in team_info.itertuples()}
