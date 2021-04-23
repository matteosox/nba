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
            "logos/*",
            "teams.yaml",
            "blackontrans.mplstyle",
            "logging.yaml",
            "settings.toml",
        ],
    },
    python_requires=">=3.8",
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
        "dynaconf",
        "awswrangler",
        "boto3",
    ],
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
