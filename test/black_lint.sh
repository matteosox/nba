#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Black formatting for git sha $GIT_SHA"

USER_ID=$(id -u "$USER")

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    -e LOCAL_USER_ID="$USER_ID" \
    -v "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    black --verbose nba
