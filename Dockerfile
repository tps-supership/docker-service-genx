FROM python:2.7-alpine

MAINTAINER tPS <thomas.yoshihara@supership.jp>

RUN apk update && \
    apk add bash

ADD sites-enabled/ /etc/nginx/sites-enabled/

VOLUME ["/etc/nginx/sites-enabled/"]

ADD update.py /

