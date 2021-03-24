#! /usr/bin/env bash
set -euf -o pipefail

# Updates the CHANGELOG.md & VERSION files

DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

cd $DIR/../

echo "Current version:"
cat pynba/VERSION
changelog suggest > pynba/VERSION
echo "Bumping version to:"
cat pynba/VERSION
echo "Updating CHANGELOG.md"
changelog release --yes
echo "All done!"
