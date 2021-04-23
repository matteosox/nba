#! /usr/bin/env bash
set -euf -o pipefail

# Updates the requirements.txt file

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

pip-compile --generate-hashes --allow-unsafe -v "$DIR"/requirements.in > "$DIR"/requirements.txt
