#! /usr/bin/env bash
set -euf -o pipefail

GIT_SHA=$(git rev-parse --short HEAD)
echo "Black formatting for git sha $GIT_SHA"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-"$GIT_SHA" \
    black --verbose nba
