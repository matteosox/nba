#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Black formatting for git sha $GIT_SHA"

LOCAL_USER_ID=$(id -u)
LOCAL_GROUP_ID=$(id -g)

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    --user "$LOCAL_USER_ID:$LOCAL_GROUP_ID" \
    --volume "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    black --verbose nba
