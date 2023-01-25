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


import yaml
import os

from . import globals
from . import er


class Host():
    def __init__(self, host, port, username, password=None, key=None, coding='utf-8'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.key = key
        self.coding = coding

    def __dict__(self):
        return {'host': self.host, 'port': self.port,
                'username': self.username, 'password': self.password,
                'key': self.key, 'coding': self.coding}

    def to_conf(self):
        t = {'host': self.host, 'port': self.port,
             'username': self.username, 'coding': self.coding}
        if self.password:
            t['password'] = self.password
        elif self.key:
            t['key'] = self.key
        else:
            raise er.PwdAndKeyCannotBeEmpty
        return t


class Conf():
    # 封装配置文件
    def __init__(self):
        self.C = None

    def open(self):
        if self.C == None:
            if not os.path.isfile(globals.confFileName):
                raise er.ThisIsNotDropsProject
            with open(globals.confFileName) as fd:
                self.C = yaml.load(fd.read(), Loader=yaml.Loader)
            if type(self.C) is not dict:
                raise er.ConfigurationFileFormatError
            if self.C.get('hosts', None) == None:
                self.C['hosts'] = {}
            return self

    def setProjectName(self, n):
        self.open()
        # 设置项目名
        p = self.C.get('project', {})
        p['name'] = n
        self.C['project'] = p
        self.save()
        return self

    def getProjectName(self):
        self.open()
        # TODO 0.1.6 之前项目名用的文件夹名，做个兼容。
        if 'project' not in self.C:
            n = os.path.split(os.getcwd())[-1]
            self.setProjectName(n)
            self.save()
        return self.C['project']['name']

    def save(self):
        with open(globals.confFileName, 'w') as fd:
            fd.write(yaml.dump(self.C))
        return self

    def new(self):
        if os.path.isfile(globals.confFileName):
            raise er.ConfigFileAlreadyExists
        self.C = {'hosts': {}}
        self.save()
        return self

    def add_host(self, hostAlias, host, port=22, username='root', password=None, key=None, coding='utf-8'):
        # 增加 主机配置。coding 为服务器 shell 编码
        self.open()
        h = Host(host, port, username, password, key, coding)
        self.C['hosts'][hostAlias] = h.to_conf()
        self.save()
        return self

    def change_host(self, hostAlias, host, port=22, username='root', password=None, key=None, coding='utf-8'):
        # 修改 host
        self.open()
        h = Host(host, port, username, password, key, coding)
        self.C['hosts'][hostAlias] = h.to_conf()
        self.save()
        return self

    def drop_host(self, hostAlias):
        # 移除 host
        self.open()
        if hostAlias in self.C['hosts']:
            self.C['hosts'].pop(hostAlias)
        else:
            raise er.HostDoesNotExist(hostAlias)
        self.save()
        return self

    def print_minlength(self, s, length):
        # 最小打印长度
        ind = 0
        while True:
            l = ind + length - len(s)
            if l < 0:
                ind += length
            else:
                ind += l
                break
        return s + ind * ' '

    def print_host(self, n, host, head=''):
        print(head, n)
        for k, i in host.items():
            p = self.print_minlength(k, 12)
            if k == 'password':
                print(head, '    ', p, ' *')
            else:
                print(head, '    ', p, i)

    def print_hosts(self, n, hs, head=''):
        print(head, n)
        for h, item in hs.items():
            self.print_host(h, item, head+'    ')

    def ls(self, host=None):
        # 输出 host
        self.open()

        if host is None:
            self.print_hosts(self.C['hosts'])
            return self

        self.print_host(host, self.C['hosts'][host])
        return self

    def get_host(self, host_type):
        # 获取单个 host
        self.open()
        if host_type in self.C['hosts']:
            return Host(**self.C['hosts'][host_type])
        raise er.HostDoesNotExist(host_type)
