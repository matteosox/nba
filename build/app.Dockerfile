# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages
COPY build/install_packages.sh /usr/local/bin/install_packages.sh
RUN install_packages.sh curl ca-certificates gosu

# Install node
COPY build/install_node.sh /usr/local/bin/install_node.sh
RUN install_node.sh

# Create app user & switch to it
ENV USER=app
RUN groupadd "$USER" && useradd --shell /bin/bash --uid 1024 --create-home -g "$USER" "$USER"
USER "$USER"
WORKDIR /home/"$USER"

# Install npm packages
COPY --chown="$USER" app/package.json app/package-lock.json app/
RUN --mount=type=cache,target=/home/app/.npm,uid=1024 npm --prefix app install

# Setup entrypoint for optional custom user id configuration
COPY build/entrypoint.sh /usr/local/bin/entrypoint.sh
USER root
ENTRYPOINT [ "entrypoint.sh" ]
CMD ["bash"]
