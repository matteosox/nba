#! /usr/bin/env bash
set -ef -o pipefail

# Push step for CICD

GIT_SHA=$(git rev-parse --short HEAD)
echo "Pushing images for git sha $GIT_SHA"
export DOCKER_BUILDKIT=1

docker push matteosox/nba:notebook-"$GIT_SHA"
docker push matteosox/nba:app-"$GIT_SHA"

echo "All done!"
