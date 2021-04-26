#! /usr/bin/env bash
set -ef -o pipefail

# Build the Next.js web app

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

GIT_SHA=$(git rev-parse --short HEAD)
echo "Building the Next.js app for git sha $GIT_SHA"

app/run.sh --no-browser npm --prefix app run build

echo "All done!"
