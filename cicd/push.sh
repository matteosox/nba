#! /usr/bin/env bash
set -euf -o pipefail

# Push step for CI

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

GIT_SHA=$(git rev-parse --short HEAD)
echo "Pushing images for git sha $GIT_SHA"
export DOCKER_BUILDKIT=1

docker push matteosox/nba-notebook:"$GIT_SHA"
docker push matteosox/nba-app:"$GIT_SHA"

BRANCH=$(git rev-parse --abbrev-ref HEAD)
MAIN_BRANCH="main"
echo "Current branch: $BRANCH"
echo "Only push images without a tag on $MAIN_BRANCH branch"

if [[ "$BRANCH" == "$MAIN_BRANCH" ]]; then
    echo "Pushing images without a tag"
    docker tag matteosox/nba-notebook:"$GIT_SHA" matteosox/nba-notebook
    docker tag matteosox/nba-app:"$GIT_SHA" matteosox/nba-app
    docker push matteosox/nba-notebook
    docker push matteosox/nba-app
fi

echo "All done!"
