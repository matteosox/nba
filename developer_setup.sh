#! /usr/bin/env bash
set -euf -o pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE}")" && pwd)"

ln -s $DIR/test/pre-commit $DIR/.git/hooks/pre-commit
