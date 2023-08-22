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

class Environment():
    def __init__(self, host, port, username, identity_file, password, env, encoding, deploy_path, config):
        self.host = host
        self.port = port
        self.username = username
        self.identity_file = identity_file
        self.password = password
        self.env = env
        self.encoding = encoding
        self.deploy_path = deploy_path
        self.config = config
    def to_conf(self):
        return {'host':self.host,
            'port':self.port,
            'username':self.username,
            'identity_file':self.identity_file,
            'password':self.password,
            'encoding':self.encoding,
            'deploy_path':self.deploy_path,
            'config':self.config}

class Conf():
    # 封装配置文件
    def __init__(self):
        pass

    def open(self, path):
        self.path = path
        with open(path) as fd:
            c = yaml.load(fd.read(), Loader=yaml.Loader)
        if 'project' not  in c:
            raise er.ConfigurationFileMissObj('project')
        if 'name' not in c['project']:
            raise er.ConfigurationFileMissObj('project.name')
        if 'env' not in c:
            c['env'] = {}
        self._data = c
        return self

    # 方便获取配置对象
    def __getattr__(self, name):
        if name == 'env':
            return {k:Environment(i) for k, i in  self._data['env'].items()}
        return self._data[name].copy()

    def set_project_name(self, n):
        self.open()
        # 设置项目名
        p = self._data.get('project', {})
        p['name'] = n
        self._data['project'] = p
        self.save()
        return self

    def save(self):
        with open(globals.config_file, 'w') as fd:
            fd.write(yaml.dump(self._data))
        return self

    def new(self):
        if os.path.isfile(globals.config_file):
            raise er.ConfigFileAlreadyExists
        self._data = {'env': {}}
        self.save()
        return self

    def set_env(self, name, env:Environment):
        self._data['env'][name] = env.to_conf()
    def remove_env(self, name):
        del(self._data['env'][name])

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

    def print_host(self, name, hostinfo, head=''):
        print(head + name + ':')
        for k, i in hostinfo.items():
            p = self.print_minlength(k, 12)
            if k == 'password':
                print(head + '  ' + p, ' *')
            else:
                print(head + '  ' + p, i)

    def print_env(self, env, head=''):
        print(head + 'env:')
        for h, item in env.items():
            self.print_host(h, item, head+'  ')

    def ls(self, host=None):
        # 输出 host
        self.open()
        if host is None:
            self.print_env(self._data['env'])
            return self

        self.print_host(host, self._data['env'][host])
        return self

    def get_env(self, name) -> Environment:
        # 获取单个 env
        self.open()
        if name in self._data['env']:
            return Environment(**self._data['env'][name])
        raise er.EnvDoesNotExist(name)
