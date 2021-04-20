#! /usr/bin/env bash
set -euf -o pipefail

# Runs etl commands in the notebook container

GIT_SHA=$(git rev-parse --short HEAD)
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"
LOCAL_ENV_OPTION=""

usage()
{
    echo "usage: ./run.sh [--git-sha -g sha=$GIT_SHA] [--env -e env] [--local-env -l] CMD"
}

while true; do
    if [[ $# -eq 0 ]]; then
        echo "No command provided, see below"
        usage
        exit 2
    fi
    case "$1" in
        -g | --git-sha )
            GIT_SHA="$2"
            echo "Using custom git sha \"$GIT_SHA\""
            shift 2
            ;;
        -e | --env )
            export ENV_FOR_DYNACONF="$2"
            echo "Using dynaconf environment \"$ENV_FOR_DYNACONF\""
            shift 2
            ;;
        -l | --local-env )
            LOCAL_ENV_OPTION="--env-file $DIR/../build/notebook.local.env"
            echo "Loading local environment parameters"
            shift
            ;;
        -h | --help )
            usage
            exit
            ;;
        -* )
            echo "Invalid option provided, see below"
            usage
            exit 2
            ;;
        * )
            CMD="$@"
            break
            ;;
    esac
done


CMD="$@"
echo "Running ${CMD} in the notebook container"

docker run --rm \
    --name etl \
    --env-file $DIR/../build/notebook.env \
    $LOCAL_ENV_OPTION \
    -v $DIR/../data:/home/jupyter/nba/data \
    matteosox/nba:notebook-"$GIT_SHA" \
    $CMD