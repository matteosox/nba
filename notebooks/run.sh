#! /usr/bin/env bash
set -ef -o pipefail

# Opens up a Jupyter notebook in a Docker container

TAG=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

PORT=8888
IP=0.0.0.0

usage()
{
    echo "usage: ./run.sh [--ip -i ip=$IP] [--port -p port=$PORT] [--tag -t sha=$TAG]"
}

while [ "$1" != "" ]; do
    case $1 in
        -t | --tag )            shift
                                TAG=$1
                                ;;
        -i | --ip )             shift
                                IP=$1
                                ;;
        -p | --port )           shift
                                PORT=$1
                                ;;
        -h | --help )           usage
                                exit
                                ;;
        * )                     usage
                                exit 1
    esac
    shift
done

echo "Opening up a Jupyter notebook in your browser at http://$IP:$PORT for tag $TAG"

open_browser() {
    sleep 2
    python -m webbrowser http://$IP:$PORT
}

open_browser &
docker run --rm \
    -p $PORT:$PORT \
    --name notebook \
    -v $DIR/../:/home/jupyter/nba \
    notebook:$TAG \
    jupyter notebook \
    --ip=$IP \
    --no-browser \
    --NotebookApp.token='' \
    --NotebookApp.notebook_dir=/home/jupyter/nba/notebooks \
    --port=$PORT
