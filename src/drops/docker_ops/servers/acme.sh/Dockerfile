FROM alpine:3.16

RUN apk add --no-cache -U \
    docker-compose \
    openssl \
    openssh-client \
    coreutils \
    bind-tools \
    curl \
    sed \
    socat \
    tzdata \
    oath-toolkit-oathtool \
    tar \
    libidn \
    jq

COPY bin/install_acme_sh /usr/local/bin
COPY bin/redeploy_key /usr/local/bin

# 原本的 crond 有 run-parts 命令，删掉。不然会影响脚本运行。
RUN echo > /var/spool/cron/crontabs/root && \
    install_acme_sh

CMD redeploy_key && crond -f -d 8