#! /usr/bin/env bash
set -euf -o pipefail

curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -
./install_packages.sh nodejs
