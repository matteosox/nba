#! /usr/bin/env bash
set -euf -o pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

echo "Setting up git pre-commit hook"
ln -s "$REPO_DIR"/test/pre-commit "$REPO_DIR"/.git/hooks/pre-commit

echo "Since git only stores a single executable bit for file permissions, we'll need to configure file permissions as well."
build/set_file_permissions.sh

echo "With that out of the way, let's setup and test the repo"
cicd/setup.sh
cicd/test.sh

echo "That seems to have worked. Vercel builds the Next.js app for us in CI, but we can also do that locally."
echo "Let's test that out."
app/build.sh

echo "All done setting up and running tests, now time to try updating the requirements."
echo "NOTE: This will edit the repo, but no need to keep those edits."
requirements/update_requirements_inside_docker.sh

echo "Next up, we'll run the app locally."
echo "Once you're happy with the result, hit ctrl-c to continue to the next step."
app/run.sh

echo "Moving on to the final step: running the Jupyter notebook environment."
echo "Again, once you're happy with the result, hit ctrl-c."
notebooks/run.sh
