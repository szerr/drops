FROM alpine:3.16

RUN apk add --no-cache -U rsync openssh-client mariadb-client coreutils xz python3  py3-pip && pip3 install paramiko pyyaml

COPY ./src/drops  /usr/lib/drops/drops
COPY ./src/drops/drops.py  /usr/bin/drops

ENV PYTHONPATH=/usr/lib/drops/

CMD crond -f -d 8