FROM python:3.10.4-slim-bullseye
MAINTAINER asdx 

ENV TINI_VERSION="v0.19.0"

ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini

WORKDIR /app
COPY . .

RUN pip install -U pip setuptools wheel && \
    pip install -r requirements.txt && \
    useradd -m -r mercury && \
    chmod +x /tini

USER mercury

ENTRYPOINT ["/tini", "--"]
