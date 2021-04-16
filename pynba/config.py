"""Config for pynba package"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Dataclass containing configuration"""

    aws_s3_region: str = "us-west-2"
    aws_s3_bucket: str = "nba-mattefay"
    aws_s3_key_prefix: str = "prod"
    local_data_directory: str = "/home/jupyter/nba/notebooks/data"
    pbpstats_directory: str = "pbpstats"
    possessions_directory: str = "possessions"
    seasons_directory: str = "seasons"
    teams_directory: str = "teams"
    plots_directory: str = "plots"
    pymc3_random_seed: int = 42
