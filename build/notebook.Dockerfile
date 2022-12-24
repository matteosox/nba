# syntax=docker/dockerfile:1.4
FROM ubuntu:22.04

# Install OS-level packages
COPY build/install_packages.sh build/install_fonts.sh /usr/local/bin/
RUN install_packages.sh \
    python3.10-dev \
    python3.10-venv \
    g++ \
    libopenblas-dev \
    git \
    awscli \
    libyaml-dev \
    shellcheck && \
    install_fonts.sh

# Move to home directory
WORKDIR /root

# Create and activate virtual environment
ENV VIRTUAL_ENV=/root/.venv
RUN python3.10 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies
COPY requirements/requirements.txt "$VIRTUAL_ENV"
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip wheel setuptools && \
    pip install --requirement "$VIRTUAL_ENV"/requirements.txt

# Move to repo directory
WORKDIR /root/nba

# Copy over source code and packaging files
COPY pynba pynba
COPY pyproject.toml ./

# Install package using pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --editable .

# Trust repo directory
RUN git config --global --add safe.directory /root/nba

# Pass Git SHA in
ARG GIT_SHA
ENV PYNBA_GIT_SHA=$GIT_SHA
