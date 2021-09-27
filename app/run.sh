#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
CMD=(npm --prefix app run dev)
BROWSER=true
PORT=3000

usage()
{
    echo "usage: run.sh [--git-sha -g sha=$GIT_SHA] [--no-browser -n] [--port -p port=$PORT] cmd=${CMD[*]}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -g | --git-sha )
            GIT_SHA="$2"
            shift 2
            ;;
        -n | --no-browser )
            BROWSER=false
            shift
            ;;
        -p | --port )
            PORT="$2"
            shift 2
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

open_browser() {
    sleep 2
    python -m webbrowser http://localhost:"$PORT"
}

if "$BROWSER"; then
    open_browser &
fi

docker run --rm \
    --publish "$PORT":"$PORT" \
    --env-file build/app.local.env \
    --env PORT="$PORT" \
    --volume "$REPO_DIR"/app:/home/app/app \
    --volume /home/app/app/node_modules \
    matteosox/nba-app:"$GIT_SHA" \
    "${CMD[@]}"
