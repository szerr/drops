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
    'drops host add ssh.example.com 22 -k ~/.ssh/id_ed25519',
    'drops initDebianEnv',
    'drops project name test',
    'drops deploy',
    'curl http://ssh.example.com',
    'drops nginxReload',
    'drops nginxForceReload',
    'drops stop -s nginx',
    'drops start -s nginx',
    'drops kill -s nginx',
    'drops rm -s nginx -f',
    'drops up',
    'drops restart -s nginx',
    'drops stop',
    'drops rm -f',
    'drops undeploy -f',
]


class BinErr(Exception):
    def __str__(self):
        return self.args[0]


def testBin(b):
    s = os.system(b)
    if s != 0:
        raise BinErr(b)


def main():
    pwd = os.getcwd()
    if os.path.isdir(testProjectName):
        shutil.rmtree(testProjectName)

    testBin('drops new ' + testProjectName)
    os.chdir(testProjectName)
    for b in binLi:
        print('============', b, '============')
        testBin(b)

    if os.path.isdir(testProjectName):
        shutil.rmtree(testProjectName)


if __name__ == '__main__':
    main()
