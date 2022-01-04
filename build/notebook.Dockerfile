# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages
COPY build/install_packages.sh /usr/local/bin/install_packages.sh
RUN install_packages.sh python3-dev python3-venv g++ libopenblas-dev git awscli libyaml-dev shellcheck
COPY build/install_fonts.sh /usr/local/bin/install_fonts.sh
RUN install_fonts.sh

# Create Jupyter notebook user & switch to it
ENV USER=jupyter
RUN groupadd --gid 1024 "$USER" && useradd --shell /bin/bash --uid 1024 --create-home --gid 1024 "$USER"
USER "$USER"
WORKDIR /home/"$USER"

# Create and activate virtual environment
ENV VIRTUAL_ENV=/home/"$USER"/.venv
RUN python3 -m venv "$VIRTUAL_ENV"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies
RUN mkdir -p .cache/pip
COPY --chown="$USER" requirements/requirements.txt "$VIRTUAL_ENV"
RUN --mount=type=cache,target=/home/jupyter/.cache/pip,uid=1024,gid=1024 \
    pip install --upgrade pip wheel setuptools && \
    pip install --requirement "$VIRTUAL_ENV"/requirements.txt

# Copy over source code and packaging files
COPY --chown="$USER" pynba nba/pynba
COPY --chown="$USER" setup.py nba/setup.py

# Install package using pip
RUN pip install --editable nba/.

# Pass Git SHA in
ARG GIT_SHA
ENV PYNBA_GIT_SHA=$GIT_SHA
