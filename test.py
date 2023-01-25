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

testProjectName = 'te'

binLi = [
    'drops --debug host add test example.com 3003 -k ~/.ssh/id_ed25519',
    'drops --debug initDebianEnv',
    'drops --debug project name drops',
    'drops --debug sync',
    'drops --debug sync volumes',
    'drops --debug sync var',
    'drops --debug deploy',
    'curl http://example.com',
    'drops --debug nginxReload',
    'drops --debug nginxForceReload',
    # 'drops --debug deployHttpsKey',
    'drops --debug stop nginx',
    'drops --debug start nginx',
    'drops --debug kill nginx',
    'drops --debug rm nginx -f',
    'drops --debug up',
    'drops --debug restart nginx',
    'drops --debug stop',
    'drops --debug rm -f',
    'drops --debug backup all -d %Y-%m-%d_%H:%M:%S -k 1',
    'drops --debug undeploy -f',
]


class BinErr(Exception):
    def __str__(self):
        return self.args[0]


def testBin(b):
    s = os.system(b)
    if s != 0:
        raise BinErr(b)


def main():
    if os.path.isdir(testProjectName):
        shutil.rmtree(testProjectName)

    testBin('drops new ' + testProjectName)
    os.chdir(testProjectName)
    for b in binLi:
        print('============', b, '============')
        testBin(b)

    # if os.path.isdir(testProjectName):
        # shutil.rmtree(testProjectName)


if __name__ == '__main__':
    main()
