#! /usr/bin/env bash
set -euf -o pipefail

TAG=$(git rev-parse --short HEAD)
echo "Running app for tag $TAG"
DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

docker run -p 3000:3000 -v $DIR:/home/app app:$TAG npm run dev
