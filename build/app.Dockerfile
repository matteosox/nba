# syntax=docker/dockerfile:1.4
FROM ubuntu:22.04

# Install OS-level packages
COPY build/install_packages.sh build/install_node.sh /usr/local/bin/
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    install_node.sh

# Move to app directory
WORKDIR /root/nba/app

# Install npm packages
COPY app/package.json app/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm install
