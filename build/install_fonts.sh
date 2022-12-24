#! /usr/bin/env bash
set -o errexit -o nounset -o pipefail
IFS=$'\n\t'

# Installs the ttf-mscorefonts-installer package, which requires some fanciness to agree to the
# end user license agreement automatically. Inspired by:
# https://askubuntu.com/questions/16225/how-can-i-accept-the-microsoft-eula-agreement-for-ttf-mscorefonts-installer/25614#25614

echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
install_packages.sh ttf-mscorefonts-installer
