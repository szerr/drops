#!/usr/bin/python3

import os

# 对多个项目做备份


class CmdRunError(Exception):
    def __str__(self):
        return "命令执行错误: "+self.args[0]


backupBin = 'drops backup -c -d %Y-%m-%d -t /srv/backup  -f'

os.chdir('/srv/drops/')
for p in os.listdir('.'):
    if os.path.isdir(p):
        print('-------------', p, '--------------')
        os.chdir(p)
        s = os.system(backupBin)
        if s != 0:
            raise CmdRunError(backupBin)
        os.chdir('..')
