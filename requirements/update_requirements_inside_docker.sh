#! /usr/bin/env bash
set -euf -o pipefail

# Runs requirements/update_requirements.sh inside the notebook docker container

GIT_SHA=$(git rev-parse --short HEAD)
echo "Updating requirements for git sha $GIT_SHA"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run \
    --rm \
    -v "$DIR"/../:/home/jupyter/nba \
    -e "LC_ALL=C.UTF-8" \
    -e "LANG=C.UTF-8" \
    matteosox/nba:notebook-$GIT_SHA \
    ./nba/requirements/update_requirements.sh
