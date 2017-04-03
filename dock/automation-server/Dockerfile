FROM jenkins

MAINTAINER Andriy Shapochka <ashapochka@gmail.com>

USER root

COPY ./sources.list /etc/apt/
RUN apt-get update && apt-get install -yq --force-yes --no-install-recommends \
    apt-utils \
    apt-transport-https \
    ca-certificates \
    sudo
RUN echo "jenkins ALL=NOPASSWD: ALL" >> /etc/sudoers
RUN echo "deb http://172.17.0.1:3142/apt.dockerproject.org/repo debian-jessie main" >> /etc/apt/sources.list.d/docker.list
RUN apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
RUN apt-get update && apt-get install -yq --force-yes --no-install-recommends \
    docker-engine \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER jenkins

RUN /usr/local/bin/install-plugins.sh \
    ssh-credentials \
    mailer \
    scm-api \
    git-client \
    git \
    greenballs \
    cloudbees-folder