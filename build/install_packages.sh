#! /usr/bin/env bash
set -euf -o pipefail

# Utility for installing apt-get packages
# tidily and minimally by cleaning them up. Inspired by 
# https://pythonspeed.com/articles/system-packages-docker/

# Tell apt-get we're never going to be able to give manual
# feedback:
export DEBIAN_FRONTEND=noninteractive

# Update the package listing, so we know what package exist:
apt-get update

# Install security updates:
apt-get -y upgrade

# Install packages, without unnecessary recommended packages:
apt-get -y install --no-install-recommends "$@"

# Delete cached files we don't need anymore:
apt-get clean
rm -rf /var/lib/apt/lists/*
