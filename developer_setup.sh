#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "Setting up git pre-commit hook"
ln -s test/pre-commit .git/hooks/pre-commit

echo "Before going further, you'll need a build/notebook.local.env file."
echo "We'll create an empty one for you now, but in the future, you'll need to add your local config options (usually secrets) to it"
touch build/notebook.local.env

echo "With that out of the way, let's build and test the repo"
cicd/build.sh
cicd/test.sh

echo "All done building and running tests, now time to try updating the requirements."
echo "NOTE: This will edit the repo, but no need to keep those edits."
requirements/update_requirements_inside_docker.sh

echo "Next up, we'll run the app locally."
echo "Once you're happy with the result, hit ctrl-c to continue to the next step."
app/run.sh

echo "Moving on to the final step: running the Jupyter notebook environment."
echo "Again, once you're happy with the result, hit ctrl-c."
notebooks/run.sh
