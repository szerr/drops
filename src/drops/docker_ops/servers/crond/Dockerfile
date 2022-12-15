FROM alpine:3.16

# 为了 date -d 参数运行正常，alpine 需要添加 coreutils 包
RUN apk add --no-cache -U rsync openssh-client coreutils && \
    # alpine 没有分钟颗粒度的任务文件夹，加一个。
    mkdir /etc/periodic/minute 

COPY ./crontabs/root /var/spool/cron/crontabs

CMD crond -f -d 8