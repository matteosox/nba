#! /usr/bin/env bash
set -euf -o pipefail

# Git only tracks a single executable bit for all files, so when setting up the repo,
# we need to set file permissions manually for files we need to write to from Docker.

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"/..

# Set data directory permissions to allow r/w/e for all users
find data -type d -exec chmod 777 {} \;

# Set app/pages files to allow r/w/e for all users
chmod -R 777 app/pages/

# We generate the requirements/requirements.txt in Docker, so it must be writeable
chmod 766 requirements/requirements.txt
