#! /usr/bin/env bash
set -euf -o pipefail

# Updates the dev_requirements.txt & notebook_equirements.txt files

DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

pip-compile --generate-hashes --allow-unsafe -v "$DIR"/dev_requirements.in > "$DIR"/dev_requirements.txt
pip-compile --generate-hashes --allow-unsafe -v "$DIR"/notebook_requirements.in > "$DIR"/notebook_requirements.txt
