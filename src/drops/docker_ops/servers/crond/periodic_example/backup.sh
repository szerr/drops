#!/bin/sh

# 这是一个定时备份的脚本示例，利用 rsync 的 link-dest 做增量备份，并保留30天
# rsync 支持本地文件同步和基于 ssh 的远程文件同步
# 注意 run-parts 不支持 #!/usr/bin/env sh，要写成 #!/bin/sh
# 注意 rsync 有 --del，第一次运行先去掉避免写错路径导致文件丢失。

# 备份路径
bakPath=/srv/backup/<project>

rsync -avuzP --del \
--exclude 'sync.sh' \
--exclude 'recovery.sh' \
-e "ssh -p 22" \
--link-dest=$bakPath/`date "+%Y-%m-%d" -d "-1day"` \
<user>@<host>:/srv/volumes/<project>/ $bakPath/`date "+%Y-%m-%d"`

# 删除 30 天前的那个目录
rm -rf $bakPath/`date "+%Y-%m-%d" -d "-30day"`