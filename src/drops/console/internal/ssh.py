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
from . import config


class Client():
    def __init__(self, arg):
        self._client = None

        self.host = arg.host
        self.port = arg.port
        self.username = arg.username
        self.identity_file = arg.identity_file
        self.password = arg.password
        self.env = arg.env
        self.encoding = arg.encoding
        self.deploy_path = arg.deploy_path
        self.config = arg.config

    def _set_client(self):
        # 如果指定了 env，host、identity_file、 password 参数优先级高于 env。其他如果不是默认值，优先级高于env。
        if self.env:
            c = config.Conf().open(self.config)
            env = c.get_env(self.env)
            if not self.host:
                self.host = env.host
            if not self.identity_file and not self.password:
                if env.identity_file:
                    self.identity_file = env.identity_file
                elif env.password:
                    self.password = env.password
            
            if self.port is '22':
                self.port = env.port
            if self.username is 'root':
                self.username = env.username
            if self.config is 'utf-8':
                self.config = env.config
        
        self._client = SSHClient()
        self._client.load_system_host_keys()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if os.path.isfile('secrets/ssh/known_hosts'):
            self._client.load_system_host_keys('secrets/ssh/known_hosts')
        
        if self.identity_file != None:
            self._client.connect(
                self.host, port=self.port, username=self.username, key_filename=self.identity_file)
        elif self.password != None:
            self._client.connect(
                self.host, port=self.port, username=self.username, password=self.password)
        else:
            # 如果没有配置key，去预设的 secrets/ssh 或 ~/.ssh 寻找key。时间问题，我只用第一个匹配 id_ 的文件作为key。
            if os.path.isdir('secrets/ssh'):
                for i in os.listdir('secrets/ssh'):
                    if i.startswith('id_'):
                        self.identity_file = i
                        break
            if not self.identity_file:
                if os.path.isdir('~/.ssh'):
                    for i in os.listdir('~/.ssh'):
                        if i.startswith('id_'):
                            self.identity_file = i
                            break
            if self.identity_file:
                self._client.connect(
                    self.host, port=self.port, username=self.username, key_filename=self.identity_file)
            else:
                raise er.PwdAndKeyCannotBeEmpty

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
                so += s
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
