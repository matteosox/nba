#! /usr/bin/env bash
set -euf -o pipefail

# Runs requirements/update_requirements.sh inside the notebook docker container

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Updating requirements for git sha $GIT_SHA"

docker run \
    --rm \
    --name update_requirements \
    --volume "$REPO_DIR"/requirements:/root/nba/requirements \
    matteosox/nba-notebook:"$GIT_SHA" \
    requirements/update_requirements.sh
