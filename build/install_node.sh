#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

install_packages.sh curl ca-certificates gosu
curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
install_packages.sh nodejs
