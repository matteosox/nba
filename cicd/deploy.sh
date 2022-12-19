#! /usr/bin/env bash
set -euf -o pipefail

# Deploys app to Vercel

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)

echo "Deploying app to Vercel"

docker run --rm \
    --name deploy \
    --env VERCEL_DEPLOY_HOOK_URL \
    --env VERCEL_ACCOUNT_TOKEN \
    --volume "$REPO_DIR":/root/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    cicd/deploy.py
