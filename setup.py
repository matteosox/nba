"""Install pynba Python package"""

import os

from setuptools import setup, find_packages


def dir_path():
    """Get directory of this file"""
    return os.path.dirname(os.path.realpath(__file__))


def get_version():
    """Get version of this package"""
    version_path = os.path.join(dir_path(), "pynba", "VERSION")
    with open(version_path) as version_file:
        return version_file.read().strip()


setup(
    name="pynba",
    version=get_version(),
    description="NBA python package",
    author="Matt Fay",
    author_email="matt.e.fay@gmail.com",
    url="https://github.com/matteosox/nba",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_data={
        "pynba": [
            "VERSION",
            "logos/*",
            "teams.yaml",
            "blackontrans.mplstyle",
            "logging.yaml",
        ],
    },
    install_requires=[
        "pbpstats",
        "pandas",
        "Pillow",
        "numpy",
        "setuptools",
        "pyarrow",
        "matplotlib",
        "pymc3",
        "PyYaml",
    ],
    entry_points={
        "console_scripts": [
            "create_seasons = pynba.scripts.create_seasons:main",
            "create_possessions = pynba.scripts.create_possessions:main",
            "create_teams = pynba.scripts.create_teams:main",
        ],
    },
)
