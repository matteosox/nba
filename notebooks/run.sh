#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
PORT=8889
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

docker run --rm \
    --publish "$PORT":"$PORT" \
    --privileged \
    --name notebook \
    --env-file build/notebook.env \
    --env-file build/notebook.local.env \
    --volume "$REPO_DIR":/root/nba \
    --volume /root/nba/pynba.egg-info \
    matteosox/nba-notebook:"$GIT_SHA" \
    jupyter notebook \
    --ip="$IP" \
    --no-browser \
    --NotebookApp.token='' \
    --NotebookApp.notebook_dir=/root/nba/notebooks \
    --port="$PORT" \
    --allow-root
