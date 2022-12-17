#! /usr/bin/env bash
set -euf -o pipefail

# Deploys app to Vercel

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

GIT_SHA=$(git rev-parse --short HEAD)

echo "Deploying app to Vercel"

VERCEL_DEPLOY_HOOK_URL="https://api.vercel.com/v1/integrations/deploy/prj_u9E8EAUMVH5JhnXa5S6eX3gQ86aF/xUZ0rFBa2W"
VERCEL_ACCOUNT_TOKEN="UsiGHtvcYrQU7ZSqLnUENTsk"
export VERCEL_DEPLOY_HOOK_URL VERCEL_ACCOUNT_TOKEN

docker run --rm \
    --name deploy \
    --env VERCEL_DEPLOY_HOOK_URL \
    --env VERCEL_ACCOUNT_TOKEN \
    --volume "$REPO_DIR":/root/nba \
    matteosox/nba-notebook:"$GIT_SHA" \
    cicd/deploy.py
