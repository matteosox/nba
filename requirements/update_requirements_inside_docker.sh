#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Updating requirements for git sha $GIT_SHA"

docker run \
    --rm \
    --name update_requirements \
    --volume "$REPO_DIR":/root/nba \
    --volume /root/nba/pynba.egg-info \
    matteosox/nba-notebook:"$GIT_SHA" \
    requirements/update_requirements.sh
