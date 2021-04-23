#! /usr/bin/env bash
set -euf -o pipefail

GIT_SHA=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD=(npm run dev)

usage()
{
    echo "usage: ./run.sh [--git-sha -g sha=$GIT_SHA] cmd=${CMD[*]}"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -g | --git-sha )
            GIT_SHA="$2"
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
    python -m webbrowser http://localhost:3000
}

open_browser &
docker run -it --rm \
    -p 3000:3000 \
    -v "$DIR":/home/app \
    -v /home/app/node_modules \
    -v /home/app/.next \
    matteosox/nba:app-"$GIT_SHA" \
    "${CMD[@]}"
