# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages needed for the base image
COPY build/install_packages.sh /usr/local/bin/install_packages.sh
RUN install_packages.sh curl ca-certificates gosu

# Install node
COPY build/install_node.sh /usr/local/bin/install_node.sh
RUN install_node.sh

# Create app user & switch to it
ENV USER=app
RUN groupadd app && useradd --shell /bin/bash --uid 1024 --create-home -g app app
USER "$USER"
WORKDIR /home/"$USER"

# Install npm packages
COPY --chown="$USER" app/package.json app/package-lock.json ./
RUN mkdir node_modules && npm install

# Setup entrypoint for optional custom user id configuration
COPY --chown="$USER" build/entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT [ "entrypoint.sh" ]
CMD ["bash"]
