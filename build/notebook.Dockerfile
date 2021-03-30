FROM ubuntu:20.04

# Install apt-get packages needed for the base image
COPY build/install_packages.sh .
RUN ./install_packages.sh python3-dev python3-pip python3-venv build-essential libmkl-dev libopenblas-dev git

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
RUN pip install --upgrade pip wheel setuptools && pip install -r notebook_requirements.txt

# Copy over source code and packaging files
RUN mkdir nba
COPY pynba nba/pynba
COPY setup.py nba/setup.py

# Install package using pip config to pickup dependencies
RUN pip install --editable nba/.
 