#! /usr/bin/env bash
set -euf -o pipefail

TAG=$(git rev-parse --short HEAD)
echo "Running tests for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$TAG \
    black --verbose --check nba

echo "Running pylint"
docker run \
    --rm \
    --name pylint \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$TAG \
    pylint --rcfile nba/pylintrc nba

echo "Running Python unit tests"
docker run \
    --rm \
    --name python_unit_test \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$TAG \
    python -m unittest discover --verbose --start-directory nba
