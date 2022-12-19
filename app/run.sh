#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
CMD=(npm run dev)
PORT=3000

usage()
{
    echo "usage: run.sh [--git-sha -g sha=$GIT_SHA] [--port -p port=$PORT] cmd=${CMD[*]}"
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

docker run --rm \
    --name app \
    --publish "$PORT":"$PORT" \
    --env-file build/app.local.env \
    --env PORT="$PORT" \
    --volume "$REPO_DIR"/app:/home/app/app \
    --volume "$REPO_DIR"/data:/home/app/data \
    --volume /home/app/app/node_modules \
    matteosox/nba-app:"$GIT_SHA" \
    "${CMD[@]}"
