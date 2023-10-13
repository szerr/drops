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
import sys
import shutil
import atexit

test_project_name = 'te'
start_dir = os.getcwd()

remote_bin = [
    # 远程部署
    '-e dev -H example.drops.icu env add',
    'env ls',
    '-e dev env change',
    '-e dev env remove',
    '-H example.drops.icu -p 22 -u root -i ~/.ssh/id_ed25519 -P 1 -e dev -E utf-8 -d /srv/drops/test -c drops.yaml env add',
    'env ls',
    # '-e dev init-debian-env',
    'project name example',
    'build server',
    '-e dev sync -f',
    '-e dev sync volumes -f',
    '-e dev sync -f var',
    '-e dev deploy',
    'ps',
    '-e dev nginx-reload',
    '-e dev nginx-force-reload',
    # 'deployHttpsKey',
    '-e dev stop nginx',
    '-e dev start nginx',
    '-e dev logs nginx',
    '-e dev kill nginx',
    '-e dev rm nginx -f',
    '-e dev up',
    '-e dev restart nginx',
    '-e dev stop',
    '-e dev rm -f',
    '-e dev backup all -d %Y-%m-%d_%H:%M:%S -k 1',
    '-e dev backup all -c -d %Y-%m-%d -t ./backup',
    '-e dev undeploy -f',
]

local_bin = [
    # 本地部署
    'up',
    'ps',
    'build server',
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

docker_bin = [
    'build -t szerr/drops:dev ../../../..',
    'run --rm --mount type=bind,source=`pwd`,target=/srv/drops szerr/drops:dev drops version'
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
    b = 'python3 main.py --debug new ' + test_project_name
    print(b)
    s = os.system(b)
    atexit.register(lambda: '-c' in sys.argv[1:] and clear())
    if s != 0:
        print('create project error.')
        return

    global remote_bin, local_bin, docker_bin
    remote_bin = ['python3 ../main.py --debug ' + i for i in remote_bin]
    local_bin = ['python3 ../main.py --debug ' + i for i in local_bin]
    docker_bin = ['docker ' + i for i in docker_bin]

    os.chdir(test_project_name)
    if 'remote' in sys.argv[1:]:
        binLi = remote_bin
    elif 'local' in sys.argv[1:]:
        binLi = local_bin
    elif 'docker' in sys.argv[1:]:
        binLi = docker_bin
    else:
        binLi = remote_bin + local_bin + docker_bin

    for b in binLi:
        print('run>', b)
        s = os.system(b)
        if s != 0:
            break


if __name__ == '__main__':
    main()
