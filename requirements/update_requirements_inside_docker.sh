#! /usr/bin/env bash
set -euf -o pipefail

# Runs requirements/update_requirements.sh inside the dev docker container

TAG=$(git rev-parse --short HEAD)
echo "Updating requirements for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run \
    --rm \
    -v "$DIR"/../:/home/dev/nba \
    -e "LC_ALL=C.UTF-8" \
    -e "LANG=C.UTF-8" \
    dev:$TAG \
    ./nba/requirements/update_requirements.sh
