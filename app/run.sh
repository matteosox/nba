#! /usr/bin/env bash
set -ef -o pipefail

TAG=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
CMD="npm run dev"

usage()
{
    echo "usage: ./run.sh [--tag -t sha=$TAG] [--command -c cmd=$CMD"
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

docker run -p 3000:3000 -v "$DIR":/home/app app:"$TAG" $CMD
