#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

echo "Setting up git pre-commit hook"
ln -s $DIR/test/pre-commit $DIR/.git/hooks/pre-commit

echo "First off, we'll build and test the repo"
$DIR/cicd/build.sh
$DIR/cicd/test.sh

echo "All done building and running tests, now time to try updating the requirements."
echo "NOTE: This will edit the repo, but no need to keep those edits."
$DIR/requirements/update_requirements_inside_docker.sh

echo "OK, that seems to have worked. Now let's see if you can update the CHANGELOG.md and VERSION files."
echo "NOTE: Again, this will change some files, but no need to keep the changes."
$DIR/docs/release_inside_docker.sh

echo "Next up, we'll run the app locally."
echo "Once you're happy with the result, hit ctrl-c to continue to the next step."
$DIR/app/run.sh

echo "Moving on to the final step: running the Jupyter notebook environment."
echo "Again, once you're happy with the result, hit ctrl-c."
$DIR/notebooks/run.sh
