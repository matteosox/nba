#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"/..
cd "$REPO_DIR"

pip-compile --upgrade --resolver=backtracking --generate-hashes --allow-unsafe --verbose --output-file requirements/requirements.txt requirements/requirements.in
