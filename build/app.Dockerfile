# syntax=docker/dockerfile:1.4
FROM ubuntu:22.04

# Copy over shell scripts
COPY build/install_packages.sh build/install_node.sh build/entrypoint.sh /usr/local/bin/

# Setup custom entrypoint for handling file permission stuff
ENTRYPOINT [ "entrypoint.sh" ]
CMD ["bash"]

# Install OS-level dependencies
RUN --mount=type=cache,target=/var/cache/apt \
    --mount=type=cache,target=/var/lib/apt \
    install_node.sh

# Create user and move to that directory
ENV USER=zion
RUN groupadd --gid 1000 "$USER" && useradd --shell /bin/bash --uid 1000 --create-home --gid 1000 "$USER"
WORKDIR /home/"$USER"/nba/app

# Install npm packages
COPY app/package.json app/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm install
