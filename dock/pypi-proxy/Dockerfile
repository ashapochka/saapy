FROM python:3.5.2

MAINTAINER Andriy Shapochka <ashapochka@gmail.com>

# devpi user
RUN addgroup --system --gid 1000 devpi \
    && adduser --disabled-login --system --uid 1000 --home /data --shell /sbin/nologin --group devpi

COPY ./tini /
RUN chmod +x /tini

COPY ./requirements.txt /
RUN pip install -r /requirements.txt

EXPOSE 3141
VOLUME /data

USER devpi
ENV HOME /data
WORKDIR /data

ENTRYPOINT ["/tini", "--"]
CMD ["devpi-server", "--host", "0.0.0.0", "--port", "3141"]
