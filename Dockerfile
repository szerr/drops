FROM alpine:3.16

RUN apk add --no-cache -U git bash rsync openssh-client coreutils xz python3 py3-pip sshpass && pip3 install "watchdog >= 3.0.0" "paramiko >= 2.12" "pyyaml >= 5.3"

COPY ./src/drops  /usr/lib/drops/drops
COPY ./src/drops/drops.py  /usr/bin/drops

ENV PYTHONPATH=/usr/lib/drops/

WORKDIR /srv/drops

CMD crond -f -d 8