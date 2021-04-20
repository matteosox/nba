#! /usr/bin/env bash
set -euf -o pipefail

GIT_SHA=$(git rev-parse --short HEAD)
echo "Running tests for git sha $GIT_SHA"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
EXIT_CODE=0

echo "Running Black Python linting"
BLACK_STATUS=FAIL
docker run \
    --rm \
    --name black_linting \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$GIT_SHA \
    black --verbose --check nba \
    && BLACK_STATUS=SUCCESS \
    || EXIT_CODE=1

echo "Running pylint"
PYLINT_STATUS=FAIL
docker run \
    --rm \
    --name pylint \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$GIT_SHA \
    pylint --rcfile nba/pylintrc nba \
    && PYLINT_STATUS=SUCCESS \
    || EXIT_CODE=1

echo "Running Python unit tests"
PYTHON_UNIT_TESTS_STATUS=FAIL
docker run \
    --rm \
    --name python_unit_test \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$GIT_SHA \
    python -m unittest discover --verbose --start-directory nba \
    && PYTHON_UNIT_TESTS_STATUS=SUCCESS \
    || EXIT_CODE=1

echo "Test Summary"
echo "  - Black Python Linting: $BLACK_STATUS"
echo "  - Pylint: $PYLINT_STATUS"
echo "  - Python Unit Tests: $PYTHON_UNIT_TESTS_STATUS"

exit $EXIT_CODE
