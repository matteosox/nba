#! /usr/bin/env bash
set -euf -o pipefail

# Updates the requirements.txt file

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

pip-compile --upgrade --resolver=backtracking --generate-hashes --allow-unsafe --verbose --output-file requirements/requirements.txt requirements/requirements.in
