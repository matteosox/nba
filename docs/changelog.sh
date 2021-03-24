#! /usr/bin/env bash
set -euf -o pipefail

# Updates the CHANGELOG.md

TAG=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run \
    --rm \
    --workdir /home/dev/nba \
    --name changelog_updates \
    -v "$DIR"/../:/home/dev/nba \
    dev:$TAG \
    changelog "$@"
