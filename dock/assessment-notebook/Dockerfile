FROM continuumio/anaconda3

MAINTAINER Andriy Shapochka <ashapochka@gmail.com>

USER root

RUN apt-get update --fix-missing && apt-get install -yq --force-yes --no-install-recommends \
    gcc \
    zlib1g-dev \
    libglib2.0-dev \
    libxext6 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN conda install --yes \
    pytest-pep8 \
    pytest-cov \
    pytest-cache \
    tabulate

RUN pip install \
    invoke \
    pytest-bdd \
    pytest-flakes \
    python-levenshtein \
    fuzzywuzzy \
    gitpython \
    pytest-datadir-ng \
    tox \
    jira \
    antlr4-python3-runtime \
    pyIsEmail \
    neo4j-driver \
    simpy

# Scitools Understand specific settings
ENV UND_HOME /opt/scitools
ENV PATH $PATH:$UND_HOME/bin/linux64
ENV PYTHONPATH $PYTHONPATH:$HOME:$UND_HOME/bin/linux64/python
