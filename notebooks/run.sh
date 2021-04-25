#! /usr/bin/env bash
set -euf -o pipefail

# Opens up a Jupyter notebook in a Docker container

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
PORT=8888
IP=0.0.0.0

usage()
{
    echo "usage: run.sh [--ip -i ip=$IP] [--port -p port=$PORT] [--git-sha -g sha=$GIT_SHA] [--env -e env]"
}

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -g | --git-sha )
            GIT_SHA="$2"
            shift 2
            ;;
        -i | --ip )
            IP="$2"
            shift 2
            ;;
        -p | --port )
            PORT="$2"
            shift 2
            ;;
        -e | --env )
            export ENV_FOR_DYNACONF="$2"
            echo "Using dynaconf environment \"$ENV_FOR_DYNACONF\""
            shift 2
            ;;
        -h | --help )
            usage
            exit
            ;;
        * )
            echo "Invalid inputs, see below"
            usage
            exit 1
    esac
done

echo "Opening up a Jupyter notebook in your browser at http://$IP:$PORT for git sha $GIT_SHA"

open_browser() {
    sleep 2
    python -m webbrowser http://"$IP":"$PORT"
}

open_browser &
docker run --rm \
    -p "$PORT":"$PORT" \
    --name notebook \
    --env-file build/notebook.env \
    --env-file build/notebook.local.env \
    -v "$REPO_DIR":/home/jupyter/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    jupyter notebook \
    --ip="$IP" \
    --no-browser \
    --NotebookApp.token='' \
    --NotebookApp.notebook_dir=/home/jupyter/nba/notebooks \
    --port="$PORT"
