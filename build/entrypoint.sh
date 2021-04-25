#! /usr/bin/env bash
set -euf -o pipefail

# Run with user id $LOCAL_USER_ID using gosu if it is present.
# This is a way of passing permissions for a mounted volume
# to the user running in the container. Inspired by:
# https://denibertovic.com/posts/handling-permissions-with-docker-volumes/

if [[ -z "${LOCAL_USER_ID-}" ]]; then
    exec gosu "$USER" "$@"
fi

echo "Starting with UID : $LOCAL_USER_ID"
useradd --shell /bin/bash --uid "$LOCAL_USER_ID" --non-unique -g "$USER" user

exec gosu user "$@"
