#! /usr/bin/env bash
set -euf -o pipefail

# Updates the CHANGELOG.md & VERSION files

TAG=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run \
    --rm \
    --name changelog_updates \
    -v "$DIR"/../:/home/dev/nba \
    matteosox/nba:dev-$TAG \
    nba/docs/release.sh
