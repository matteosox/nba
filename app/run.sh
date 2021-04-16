#! /usr/bin/env bash
set -ef -o pipefail

TAG=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

usage()
{
    echo "usage: ./run.sh [--tag -t sha=$TAG] [--command -c cmd]"
}

while [ "$1" != "" ]; do
    case "$1" in
        -t | --tag )
            shift
            TAG="$1"
            ;;
        -c | --command )
            shift
            CMD="$1"
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

echo "Running app for tag $TAG"

open_browser() {
    sleep 2
    python -m webbrowser http://localhost:3000
}

open_browser &
docker run -it --rm \
    -p 3000:3000 \
    -v "$DIR":/home/app \
    -v /home/app/node_modules \
    -v /home/app/.next \
    matteosox/nba:app-"$TAG" \
    $CMD
