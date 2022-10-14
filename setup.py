"""Install pynba Python package"""

from setuptools import setup, find_packages


setup(
    name="pynba",
    version="0.0.0",
    description="NBA python package",
    author="Matt Fay",
    author_email="matt.e.fay@gmail.com",
    url="https://github.com/matteosox/nba",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_data={
        "pynba": [
            "themes/*.yaml",
            "teams.yaml",
            "logging.yaml",
            "settings.toml",
        ],
    },
    entry_points={
        "console_scripts": [
            "create_seasons = pynba.scripts.create_seasons:main",
            "create_possessions = pynba.scripts.create_possessions:main",
            "create_teams = pynba.scripts.create_teams:main",
            "pynba_update = pynba.scripts.update:main",
            "pynba_sync = pynba.scripts.sync:main",
        ],
    },
)
