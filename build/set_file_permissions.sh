#! /usr/bin/env bash
set -euf -o pipefail

# Git only tracks a single executable bit for all files, so when setting up the repo,
# we need to set file permissions manually for files we need to write to from Docker.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

# Set data directory permissions to allow r/w for all users
find data -type d -exec chmod 766 {} \;

# We generate the requirements/requirements.txt in Docker, so it must be writeable
chmod 666 requirements/requirements.txt
