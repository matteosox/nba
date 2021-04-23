#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[@]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Running tests for git sha $GIT_SHA"

BLACK_STATUS="NOT STARTED"
PYLINT_STATUS="NOT STARTED"
PYTHON_UNIT_TESTS_STATUS="NOT STARTED"
SHELLCHECK_STATUS="NOT STARTED"
EXIT_CODE=0

report_status() {
    echo "Test Summary"
    echo "  - Black Python Linting: $BLACK_STATUS"
    echo "  - Pylint: $PYLINT_STATUS"
    echo "  - Python Unit Tests: $PYTHON_UNIT_TESTS_STATUS"
    echo "  - ShellCheck: $SHELLCHECK_STATUS"
}
trap report_status EXIT

echo "Running Black"
BLACK_STATUS=RUNNING
if docker run \
    --rm \
    --name black_linting \
    -v "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    black --verbose --check nba
then
    BLACK_STATUS=SUCCESS
else
    EXIT_CODE=1
    BLACK_STATUS=FAILED
fi

echo "Running Pylint"
PYLINT_STATUS=RUNNING
if docker run \
    --rm \
    --name pylint \
    -v "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    pylint --rcfile nba/pylintrc nba
then
    PYLINT_STATUS=SUCCESS
else
    EXIT_CODE=1
    PYLINT_STATUS=FAILED
fi

echo "Running Python unit tests"
PYTHON_UNIT_TESTS_STATUS=RUNNING
if docker run \
    --rm \
    --name python_unit_test \
    -v "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    python -m unittest discover --verbose --start-directory nba
then
    PYTHON_UNIT_TESTS_STATUS=SUCCESS
else
    EXIT_CODE=1
    PYTHON_UNIT_TESTS_STATUS=FAILED
fi

echo "Running ShellCheck"
SHELLCHECK_STATUS=RUNNING
if docker run \
    --rm \
    --name shellcheck \
    -v "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    nba/test/shellcheck.sh
then
    SHELLCHECK_STATUS=SUCCESS
else
    EXIT_CODE=1
    SHELLCHECK_STATUS=FAILED
fi

exit $EXIT_CODE
