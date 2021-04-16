#! /usr/bin/env bash
set -euf -o pipefail

TAG=$(git rev-parse --short HEAD)
echo "Black formatting for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

echo "Running Black Python linting"
docker run \
    --rm \
    --name black_linting \
    -v "$DIR"/../:/home/jupyter/nba \
    matteosox/nba:notebook-$TAG \
    black --verbose nba
