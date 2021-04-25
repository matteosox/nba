#! /usr/bin/env bash
set -ef -o pipefail

# Build step for CICD

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

GIT_SHA=$(git rev-parse --short HEAD)
echo "Building for git sha $GIT_SHA"
export DOCKER_BUILDKIT=1

echo "Building notebook Docker image"
docker build \
    --progress=plain \
    -t matteosox/nba-notebook:"$GIT_SHA" \
    --cache-from matteosox/nba-notebook \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    --build-arg GIT_SHA="$GIT_SHA" \
    -f build/notebook.Dockerfile \
    .

echo "Building app Docker image"
docker build \
    --progress=plain \
    -t matteosox/nba-app:"$GIT_SHA" \
    --cache-from matteosox/nba-app \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -f build/app.Dockerfile \
    .

echo "All done!"
