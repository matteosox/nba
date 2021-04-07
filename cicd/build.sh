#! /usr/bin/env bash
set -ef -o pipefail

# Build step for CICD

TAG=$(git rev-parse --short HEAD)
echo "Building for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
PUSH=false

# Simple usage instructions for this script
usage()
{
    echo "usage: $DIR/build.sh [--no-cache -n] [--push -p] [--help -h]"
}

# Parse inputs
while [ "$1" != "" ]; do
    case "$1" in
        -n | --no-cache )
            echo "Building without any docker cache"
            BUILD_ARGS="--pull --no-cache"
            ;;
        -p | --push )
            echo "Pushing images upon build completion"
            PUSH=true
            ;;
        -h | --help )
            usage
            exit
            ;;
        * )
        usage
        exit 1
    esac
    shift
done

export DOCKER_BUILDKIT=1

echo "Building dev Docker image"
docker build $BUILD_ARGS \
    --progress=plain \
    -t matteosox/nba:dev-$TAG \
    --cache-from matteosox/nba:dev-$TAG \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -f "$DIR"/../build/dev.Dockerfile \
    "$DIR"/../

echo "Building notebook Docker image"
docker build $BUILD_ARGS \
    --progress=plain \
    -t matteosox/nba:notebook-$TAG \
    --cache-from matteosox/nba:notebook-$TAG \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -f "$DIR"/../build/notebook.Dockerfile \
    "$DIR"/../

echo "Building app Docker image"
docker build $BUILD_ARGS \
    --progress=plain \
    -t matteosox/nba:app-$TAG \
    --cache-from matteosox/nba:app-$TAG \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -f "$DIR"/../build/app.Dockerfile \
    "$DIR"/../

if [ "$PUSH" = true ]; then
    echo "Pushing images"
    docker push matteosox/nba:dev-$TAG
    docker push matteosox/nba:notebook-$TAG
    docker push matteosox/nba:app-$TAG
fi

echo "All done!"
