#! /usr/bin/env bash
set -euf -o pipefail

# Normally, for a local development environment in Docker, the simplest
# way to use volume mounts to enable "editable mode", "fast refresh", etc.
# is to leave Docker in the root user and not worry about file permissions
# or ownership mounted from the git repo. Those can be a pain in the butt,
# since they depend on the developer's machine, which is a leak in the whole
# Docker container model, removing the need to worry about the details
# of anyone's computer. However, Node does not like running as root.
# More specifically, if the owner of the directory you're running next
# from doesn't match the current user, you'll get a fake permissions issue.
# To deal with that, we go through this rigamarole:
#   1) Create a user, place the repo in their home directory, but continue
# building the image as root.
#   2) Setup this entrypoint script, which in runtime will
#   3) Determine the user and group owner of the mounted repo.
#   4) Modify the existing user of the container to the new IDs
#   5) Change the owner of all files in the user's home directory.

# This has the following unfortunate side effects:
#   1) Additional complexity and size of the image, e.g. needing to install gosu,
# maintain this script, etc.
#   2) Slower runtime: this entrypoint runs every time the container is used,
#  and that slows things down.
#   3) Changes of file ownership on the developer's native machine.

REPO=/home/"$USER"/nba
USER_ID=$(stat -c "%u" "$REPO")
GROUP_ID=$(stat -c "%g" "$REPO")

echo "Reassigning user $USER to UID $USER_ID and GID $GROUP_ID"
groupmod --gid "$GROUP_ID" "$USER"
usermod --uid "$USER_ID" --gid "$GROUP_ID" "$USER"
chown -R "$USER":"$USER" /home/"$USER"

exec gosu "$USER" "$@"
