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


def get_long_description():
    """Get README.md of this package."""
    readme_path = os.path.join(dir_path(), "README.md")
    with open(readme_path, encoding="utf-8") as file_obj:
        long_description = file_obj.read()
    return long_description


setup(
    name="pynba",
    version=get_version(),
    description="NBA python package",
    long_description=get_long_description(),
    author="Matt Fay",
    author_email="matt.e.fay@gmail.com",
    url="https://github.com/matteosox/nba",
    packages=find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    package_data={
        "pynba": [
            "VERSION",
            "logos/*",
            "teams.json",
        ],
    },
    install_requires=[
        "pbpstats",
        "pandas",
        "Pillow",
        "numpy",
        "setuptools",
    ],
)
