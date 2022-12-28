#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
CMD=(npm run dev)
PORT=3000
USE_LOCAL=""

usage()
{
    echo "usage: run.sh [--git-sha -g sha=$GIT_SHA] [--port -p port=$PORT] [--local -l] cmd=${CMD[*]}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -g | --git-sha )
            GIT_SHA="$2"
            shift 2
            ;;
        -p | --port )
            PORT="$2"
            shift 2
            echo "Using custom port $PORT"
            ;;
        -l | --local )
            USE_LOCAL=true
            shift 1
            echo "Using local filesystem for plot files"
            ;;
        -h | --help )
            usage
            exit
            ;;
        -* )
            echo "Invalid option provided, see below"
            usage
            exit 1
            ;;
        * )
            IFS=" " read -r -a CMD <<< "$@"
            echo "Using custom command ${CMD[*]}"
            break
            ;;
    esac
done

echo "Running app for git sha $GIT_SHA"

export PORT USE_LOCAL

docker run --rm \
    --name app \
    --publish "$PORT":"$PORT" \
    --env-file build/app.local.env \
    --volume "$REPO_DIR":/root/nba \
    --volume /root/nba/app/node_modules \
    matteosox/nba-app:"$GIT_SHA" \
    "${CMD[@]}"
