#! /usr/bin/env bash
set -ef -o pipefail

# Build step for CICD

TAG=$(git rev-parse --short HEAD)
echo "Building for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

# Simple usage instructions for this script
usage()
{
    echo "usage: $DIR/build.sh [--cache -c cache_dir] [--no-cache -n] [--help -h]"
}

# Parse inputs
while [ "$1" != "" ]; do
    case "$1" in
        -c | --cache )
            shift
            CACHE_DIR="$1"
            echo "Using local docker build cache at $CACHE_DIR"
            TMP_CACHE=$(mktemp -d -t)
            DEV_BUILD_ARGS="--cache-from type=local,src=$CACHE_DIR/dev --cache-to type=local,mode=max,dest=$TMP_CACHE/dev --load"
            NTBK_BUILD_ARGS="--cache-from type=local,src=$CACHE_DIR/notebook --cache-to type=local,mode=max,dest=$TMP_CACHE/notebook --load"
            APP_BUILD_ARGS="--cache-from type=local,src=$CACHE_DIR/app --cache-to type=local,mode=max,dest=$TMP_CACHE/app --load"
            BUILDX_BUILDER=$(docker buildx create --use)
            docker buildx install
            cleanup() {
                docker buildx rm "$BUILDX_BUILDER"
                docker buildx uninstall
                rm -rf $CACHE_DIR
                mv $TMP_CACHE $CACHE_DIR
            }
            trap cleanup EXIT
            ;;
        -n | --no-cache )
            echo "Building without any docker cache"
            BUILD_ARGS="--pull --no-cache"
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
docker build $DEV_BUILD_ARGS \
    -t dev:$TAG \
    -f "$DIR"/../build/dev.Dockerfile \
    "$DIR"/../

echo "Building notebook Docker image"
docker build $NTBK_BUILD_ARGS \
    -t notebook:$TAG \
    -f "$DIR"/../build/notebook.Dockerfile \
    "$DIR"/../

echo "Building app Docker image"
docker build $APP_BUILD_ARGS \
    -t app:$TAG \
    -f "$DIR"/../build/app.Dockerfile \
    "$DIR"/../

echo "All done!"
