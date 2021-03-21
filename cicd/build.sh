#! /usr/bin/env bash
set -euf -o pipefail

# Builds step for CICD

TAG=$(git rev-parse --short HEAD)
echo "Building for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker build \
    -t dev:$TAG \
    -f "$DIR"/../build/dev.Dockerfile \
    "$DIR"/../

docker build \
    -t notebook:$TAG \
    -f "$DIR"/../build/notebook.Dockerfile \
    "$DIR"/../

docker build \
    -t app:$TAG \
    -f "$DIR"/../build/app.Dockerfile \
    "$DIR"/../
