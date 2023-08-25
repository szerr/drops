#!/bin/env python3

# Copyright © 2022 szerr < i@szerr.org > .

# This file is part of drops.

# drops is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.

# drops is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with drops. If not, see <https://www.gnu.org/licenses/>.

# 跑一个完整的部署测试

import os
import shutil

test_project_name = 'te'
start_dir = os.getcwd()
base_bin = 'python3 ../main.py --debug '

binLi = [
    # 远程部署
    '-e production -H example.org env add',
    'env ls',
    '-e production env change',
    '-e production env remove',
    '-H example.org -p 22 -u root -i ~/.ssh/id_ed25519 -P 1 -e production -E utf-8 -d /srv/drops -c drops.yaml env add',
    'env ls',
    '-e production init-debian-env',
    'project name example',
    '-e production sync -f',
    '-e production sync volumes -f',
    '-e production sync -f var',
    '-e production deploy',
    'ps',
    '-e production nginx-reload',
    '-e production nginx-force-reload',
    # 'deployHttpsKey',
    '-e production stop nginx',
    '-e production start nginx',
    '-e production logs nginx',
    '-e production kill nginx',
    '-e production rm nginx -f',
    '-e production up',
    '-e production restart nginx',
    '-e production stop',
    '-e production rm -f',
    '-e production backup all -d %Y-%m-%d_%H:%M:%S -k 1',
    '-e production undeploy -f',
    # 本地部署
    'up',
    'ps',
    'stop nginx',
    'start nginx',
    'logs nginx',
    'kill nginx',
    'rm nginx -f',
    'up',
    'restart nginx',
    'stop',
    'rm -f',
]


class BinErr(Exception):
    def __str__(self):
        return self.args[0]


def testBin(b):
    s = os.system(b)
    if s != 0:
        raise BinErr(b)

def clear():
    os.chdir(start_dir)
    if os.path.isdir(test_project_name):
        shutil.rmtree(test_project_name)

def main():
    s = os.system('python3 main.py --debug new ' + test_project_name)
    if s != 0:
        print('create project error.')
        clear()
        return

    os.chdir(test_project_name)
    for b in binLi:
        b = base_bin + b
        print('run>', b)
        s = os.system(b)
        if s != 0:
            break
    # clear()


if __name__ == '__main__':
    main()
