"""Config for pynba package"""

from pkg_resources import resource_filename

from dynaconf import Dynaconf

from pynba.meta_config import AbstractConfig


ENVVAR_PREFIX = "PYNBA"


class Config(AbstractConfig):  # pylint: disable=too-few-public-methods
    """Class containing configuration"""

    aws_s3_bucket: str
    aws_s3_key_prefix: str
    local_data_directory: str
    pbpstats_directory: str
    seasons_directory: str
    possessions_directory: str
    teams_directory: str
    plots_directory: str
    seasons_source: str
    possessions_source: str
    teams_source: str
    pymc3_random_seed: int
    git_sha: str


__settings = Dynaconf(
    envvar_prefix=ENVVAR_PREFIX,
    ignore_unknown_envvars=True,
    environments=True,
    settings_files=[resource_filename("pynba", "settings.toml")],
)

config = Config(__settings)
