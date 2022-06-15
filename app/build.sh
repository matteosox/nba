#! /usr/bin/env bash
set -ef -o pipefail

# Build the Next.js web app

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

app/run.sh --no-browser npm run build

echo "All done building the Next.js app!"
