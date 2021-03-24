FROM ubuntu:20.04

# Install apt-get packages needed for the base image
COPY build/install_packages.sh .
RUN ./install_packages.sh python3 python3-pip python3-venv git

# Create dev user & switch to it
RUN useradd --create-home dev
USER dev
WORKDIR /home/dev

# Create and activate virtual environment
ENV VIRTUAL_ENV=/home/dev/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install python dependencies
COPY ./requirements/dev_requirements.txt .
RUN pip install --upgrade pip wheel setuptools && pip install -r dev_requirements.txt

# Copy over source code and packaging files
RUN mkdir nba
COPY pynba nba/pynba
COPY setup.py nba/setup.py

# Install package using pip config to pickup dependencies
RUN pip install --editable nba/.
