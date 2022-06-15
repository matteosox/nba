#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
echo "Black formatting for git sha $GIT_SHA"

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    --volume "$REPO_DIR":/root/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    black --verbose .
