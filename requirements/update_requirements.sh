#! /usr/bin/env bash
set -euf -o pipefail

# Updates the requirements.txt file

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$DIR"/..
cd "$REPO_DIR"

pip-compile --generate-hashes --allow-unsafe --verbose requirements/requirements.in > requirements/requirements.txt
