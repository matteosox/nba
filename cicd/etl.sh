#! /usr/bin/env bash
set -euf -o pipefail

# Runs etl commands in the notebook container

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)
LOCAL_ENV_OPTION=()

usage()
{
    echo "usage: etl.sh [--git-sha -g sha=$GIT_SHA] [--env -e env] [--local-env -l] CMD"
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
            LOCAL_ENV_OPTION=(--env-file build/notebook.local.env)
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
            IFS=" " read -r -a CMD <<< "$@"
            break
            ;;
    esac
done

echo "Running ${CMD[*]} in the notebook container"

docker run --rm \
    --name etl \
    --env-file build/notebook.env \
    "${LOCAL_ENV_OPTION[@]}" \
    --volume "$REPO_DIR"/data:/home/jupyter/nba/data \
    matteosox/nba-notebook:"$GIT_SHA" \
    "${CMD[@]}"
