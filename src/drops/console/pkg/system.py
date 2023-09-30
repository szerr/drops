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


class SSH():
    def __init__(self, env):
        self.encoding = env.encoding
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if os.path.isfile('secret/ssh/known_hosts'):
            self._client.load_system_host_keys('secret/ssh/known_hosts')
        # 如果路径中有`~`符，替代成 $HOME
        identity_file = os.path.expanduser(env.identity_file)
        if identity_file:
            self._client.connect(
                env.host, port=env.port, username=env.username, key_filename=identity_file)
        elif env.password:
            self._client.connect(
                env.host, port=env.port, username=env.username, password=env.password)
        else:
            # 如果没有配置key，去预设的 secret/ssh 寻找。我先用第一个匹配 id_ 的文件作为key。
            if os.path.isdir('secret/ssh'):
                for i in os.listdir('secret/ssh'):
                    if i.startswith('id_'):
                        identity_file = i
                        break
            if identity_file:
                self._client.connect(
                    env.host, port=env.port, username=env.username, key_filename=identity_file)
            else:
                # 没有的话 paramiko 会寻找 ssh 预设的 key
                self._client.connect(
                    env.host, port=env.port, username=env.username)
                # raise er.PwdAndKeyCannotBeEmpty

    def exec(self, b, show=True):
        if self._client == None:
            self._set_client()
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
                so += s.decode(self.encoding)
        return so, stdout.channel.recv_exit_status()

    def exed(self, b):
        if self._client == None:
            self._set_client()
        # 返回标准输出，标准错误，状态码
        # 没有 exit 0 的话会导致命令执行随机返回 -1，貌似是 paramiko 的锅，没找到具体原因。
        stdin, stdout, stderr = self._client.exec_command(
            b + ' exit 0')
        o, e, s = stdout.read().decode(self.encoding), stderr.read().decode(
            self.encoding), stdout.channel.recv_exit_status()
        return o, e, s


def system(b):
    # os.system 在不同平台的行为不同，特别在 linux 下，是一个 16 位数，如果直接返回给 shell，会被截取低 8 位。这里做平台兼容。
    exit_code = os.system(b)
    if exit_code:
        if exit_code > 255:
            exit_code = exit_code / 256
    return int(exit_code)
