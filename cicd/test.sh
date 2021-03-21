#! /usr/bin/env bash
set -euf -o pipefail

TAG=$(git rev-parse --short HEAD)
echo "Running tests for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run \
    --rm \
    --name test \
    -v "$DIR"/../:/home/dev/nba \
    dev:$TAG \
    python -m unittest discover -v
