#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)

echo "Deploying app to Vercel"

docker run --rm \
    --name deploy \
    --env VERCEL_DEPLOY_HOOK_URL \
    --env VERCEL_ACCOUNT_TOKEN \
    --volume "$REPO_DIR":/root/nba \
    --volume /root/nba/pynba.egg-info \
    matteosox/nba-notebook:"$GIT_SHA" \
    cicd/deploy.py
