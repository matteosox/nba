# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages needed for the base image
COPY build/install_packages.sh .
RUN ./install_packages.sh curl ca-certificates

# Install node
COPY build/install_node.sh .
RUN ./install_node.sh

# Create app user & switch to it
RUN useradd --create-home app
USER app
WORKDIR /home/app

# Install npm packages
COPY --chown=app app/package.json app/package-lock.json ./
RUN mkdir node_modules && npm install

# Build app
COPY --chown=app app/. .
RUN npm run build
