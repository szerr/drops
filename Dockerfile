FROM debian:bullseye

RUN apt-get update && apt-get install ssh rsync python3-pip cron -y && apt-get clean  && pip3 install paramiko>=5.3 pyyaml>=2.12

COPY ./src/drops  /usr/lib/drops/drops
COPY ./src/drops/drops.py  /usr/bin/drops

ENV PYTHONPATH=/usr/lib/drops/

CMD cron -f