FROM ubuntu:20.04

# Install apt-get packages needed for the base image
COPY build/install_packages.sh .
RUN ./install_packages.sh build-essential curl ca-certificates
COPY build/install_node.sh .
RUN ./install_node.sh

# Create dev user & switch to it
RUN useradd --create-home app
USER app
WORKDIR /home/app
