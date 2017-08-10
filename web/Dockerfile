FROM python:2

RUN apt-get update \
    && apt-get install -y net-tools vim curl wget

ADD ./app/requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt

ADD image /

WORKDIR /
CMD ["/usr/local/bin/supervisord"]
