FROM python:3.5.2

MAINTAINER Andriy Shapochka <ashapochka@gmail.com>

USER root

COPY ./sources.list /etc/apt/

RUN apt-get update && apt-get install -yq --force-yes --no-install-recommends \
    zlib1g-dev \
    libglib2.0-dev \
    libxext6 \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN addgroup --system --gid 1000 scitools \
    && adduser --disabled-login --system --uid 1000 --home /data --shell /sbin/nologin --group scitools

COPY ./tini /
RUN chmod +x /tini

COPY ./requirements.txt /
RUN pip install -r /requirements.txt

VOLUME /data

USER scitools
ENV HOME /data
WORKDIR /data

# Scitools Understand specific settings
ENV UND_HOME $HOME/scitools
ENV PATH $PATH:$UND_HOME/bin/linux64
ENV PYTHONPATH $PYTHONPATH:$HOME:$UND_HOME/bin/linux64/python

ENTRYPOINT ["/tini", "-g", "-s", "--", "invoke"]
CMD ["--list"]
