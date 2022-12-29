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

from paramiko.client import SSHClient
import paramiko
import os

from . import er


class Client():
    def __init__(self, host, port=22, username='root', password=None, key=None, coding='utf-8'):
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if 'known_hosts' in os.listdir('.'):
            self._client.load_system_host_keys('known_hosts')
        if password != None:
            self._client.connect(
                host, port=port, username=username, password=password)
        elif key != None:
            self._client.connect(
                host, port=port, username=username, key_filename=key)
        else:
            raise er.PwdAndKeyCannotBeEmpty

        self.coding = coding

    def exec(self, b, show=True):
        # 返回标准输出，标准错误，状态码
        # 没有 exit 0 的话会导致命令执行随机返回 -1，貌似是 paramiko 的锅，没找到具体原因。
        # 为了做出类似 ssh 交互式的效果，混合了标准输出和标准错误。并在这一层做输出，屏蔽复杂度。
        # 2>&1 重定向不管用，只能 exec 重定向
        stdin, stdout, stderr = self._client.exec_command(
            'exec 2>/dev/stdout && ' + b + ' && exit 0')
        so = ''
        # 命令执行过程可能很长，所以在这里按行处理输出。
        if show:
            while True:
                s = stdout.readline()
                if s == '':
                    break
                print(s, end='')
                so += s
        else:
            while True:
                s = stdout.read()
                if s == b'':
                    break
                so += s
        return so, stdout.channel.exit_status

    def exed(self, b):
        # 返回标准输出，标准错误，状态码
        # 没有 exit 0 的话会导致命令执行随机返回 -1，貌似是 paramiko 的锅，没找到具体原因。
        stdin, stdout, stderr = self._client.exec_command(
            b + ' exit 0')
        o, e, s = stdout.read().decode(self.coding), stderr.read().decode(
            self.coding), stdout.channel.exit_status
        return o, e, s
