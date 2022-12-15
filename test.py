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

testProjectName = '_te'

binLi = [
    # 'drops host add 192.168.2.242 -p 111111',
    'drops host add ssh.example.com -k ~/.ssh/id_ed25519',
    'drops init_env_centos',
    'drops deploy',
    'drops nginx_reload',
    'drops nginx_force_reload',
    'drops stop -s nginx',
    'drops kill -s nginx',
    'drops rm -s nginx',
    'drops stop',
    'drops rm',
    'drops undeploy',
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
    try:
        testBin('drops new ' + testProjectName)
        os.chdir(testProjectName)
        for b in binLi:
            print('============', b, '============')
            testBin(b)
    except Exception as e:
        print("Fatal:", e)
        os.system('drops undeploy')
        os.chdir(pwd)
    os.chdir(pwd)
    if os.path.isdir(testProjectName):
        shutil.rmtree(testProjectName)


if __name__ == '__main__':
    main()
