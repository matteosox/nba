# syntax=docker/dockerfile:1.2
FROM ubuntu:20.04

# Install apt-get packages needed for the base image
COPY build/install_packages.sh .
RUN ./install_packages.sh python3-dev python3-pip python3-venv g++ libopenblas-dev git

# Create Jupyter notebook user & switch to it
RUN useradd --create-home jupyter
USER jupyter
WORKDIR /home/jupyter

# Create and activate virtual environment
ENV VIRTUAL_ENV=/home/jupyter/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies
COPY ./requirements/notebook_requirements.txt .
RUN mkdir .cache
RUN --mount=type=cache,target=/home/jupyter/.cache/pip,uid=1000 pip install --upgrade pip wheel setuptools && pip install -r notebook_requirements.txt

# Copy over source code and packaging files
COPY --chown=jupyter pynba nba/pynba
COPY setup.py nba/setup.py

# Install package using pip config to pickup dependencies
RUN pip install --editable nba/.
