# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages
COPY build/install_packages.sh /usr/local/bin/install_packages.sh
RUN install_packages.sh curl ca-certificates

# Install node
COPY build/install_node.sh /usr/local/bin/install_node.sh
RUN install_node.sh

# Create app user & switch to it
ENV USER=app
RUN groupadd --gid 1024 "$USER" && useradd --shell /bin/bash --uid 1024 --create-home --gid 1024 "$USER"
USER "$USER"
WORKDIR /home/"$USER"/app

# Install npm packages
COPY --chown="$USER" app/package.json app/package-lock.json ./
RUN mkdir ~/.npm
RUN --mount=type=cache,target=/home/app/.npm,uid=1024,gid=1024 \
    npm install
