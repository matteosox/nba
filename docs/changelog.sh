#! /usr/bin/env bash
set -euf -o pipefail

# Updates the CHANGELOG.md

TAG=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run \
    --rm \
    --workdir /home/jupyter/nba \
    --name changelog_updates \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$TAG \
    changelog "$@"
