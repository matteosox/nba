#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

echo "Installing apt packages"

# Ubuntu image is configured to delete cached files.
# We're using a cache mount, so we remove that config.
rm --force /etc/apt/apt.conf.d/docker-clean
echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache

# Tell apt-get we're never going to be able to give manual feedback
export DEBIAN_FRONTEND=noninteractive

# Update the package listing, so we know what package exist
apt-get update

# Install security updates
apt-get --yes upgrade

# Install packages, without unnecessary recommended packages
apt-get --yes install --no-install-recommends "$@"
