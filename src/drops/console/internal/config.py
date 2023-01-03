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

    def add_host(self, group, host, port=22, username='root', password=None, key=None, coding='utf-8'):
        # 增加 主机配置。coding 为服务器 shell 编码
        self.open()
        g = self.C['hosts'].get(group, {})
        if g is None:
            g = {}

        if host in g:
            raise er.HostExisted(host)

        h = Host(host, port, username, password, key, coding)
        g[host] = h.to_conf()
        self.C['hosts'][group] = g
        self.save()
        return self

    def change_host(self, group, host, port=22, username='root', password=None, key=None, coding='utf-8'):
        # 修改 host
        self.open()
        g = self.C['hosts'].get(group, {})
        if g is None:
            g = {}

        h = Host(host, port, username, password, key, coding)
        g[host] = h.to_conf()
        self.C['hosts'][group] = g
        self.save()
        return self

    def drop_host(self, group, host):
        # 移除 host
        self.open()
        g = self.C['hosts'].get(group, {})
        if g is None:
            g = {}

        if host in g:
            g.pop(host)
        else:
            raise er.HostNotInGroup(group, host)
        self.C['hosts'][group] = g
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

    def print_group(self, gs, head=''):
        for h, hs in gs.items():
            self.print_hosts(h, hs, head)

    def ls(self, group=None, host=None):
        # 输出 host
        self.open()
        if group == None:
            self.print_group(self.C['hosts'])
            return self

        if group not in self.C['hosts']:
            print('group "%s" does not exist' % (group))
            return self

        g = self.C['hosts'].get(group, {})

        if host is None:
            self.print_hosts(group, g)
            return self

        if host not in g:
            print('"%s" is not in group "%s"' % (host, group))
            return self
        self.print_host(host, g[host])
        return self

    def get_group(self, group):
        # 获取一个 group
        self.open()
        if group not in self.C['hosts']:
            raise er.HostGroupNotExist(group)
        return {k: Host(**i) for k, i in self.C['hosts'][group].items()}

    def get_host(self, group, host):
        # 获取单个 host
        self.open()
        gs = self.get_group(group)
        if host not in gs:
            raise er.HostNotInGroup(group, host)
        return Host(**gs[host])

    def get_hosts(self, group, hosts=[]):
        # 获取多个host，hosts 为空时返回整个 group 的 host。
        self.open()
        gs = self.get_group(group)
        if hosts:
            return {k: i for k, i in gs.items() if k in hosts}
        return gs
