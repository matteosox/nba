import os

from setuptools import setup, find_packages


def dir_path():
    return os.path.dirname(os.path.realpath(__file__))


def get_version():
    version_path = os.path.join(dir_path(), 'pynba', 'VERSION')
    with open(version_path) as version_file:
        return version_file.read().strip()


def get_long_description():
    readme_path = os.path.join(dir_path(), 'README.md')
    with open(readme_path, encoding="utf-8") as fh:
        long_description = fh.read()
    return long_description


setup(
    name='pynba',
    version=get_version(),
    description="NBA python package",
    long_description=get_long_description(),
    author='Matt Fay',
    author_email='matt.e.fay@gmail.com',
    url='https://github.com/matteosox/nba',
    packages=find_packages(
        exclude=['*.test', '*.test.*', 'test.*', 'test']
    ),
    package_data={
        'pynba': [
            'VERSION',
            'logos/*',
            'teams.json',
        ],
    },
    install_requires=[
        'pbpstats',
        'pandas',
        'Pillow',
        'numpy',
        'setuptools',
    ]
)
