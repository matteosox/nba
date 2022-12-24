#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Black formatting for git sha $GIT_SHA"

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    --volume "$REPO_DIR":/root/nba \
    --volume /root/nba/pynba.egg-info \
    matteosox/nba-notebook:"$GIT_SHA" \
    black --verbose .
