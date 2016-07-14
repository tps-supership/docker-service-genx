FROM python:2.7

MAINTAINER tPS <thomas.yoshihara@supership.jp>

ADD sites-enabled/ /etc/nginx/sites-enabled/

VOLUME ["/etc/nginx/sites-enabled/"]

ADD update.py /

