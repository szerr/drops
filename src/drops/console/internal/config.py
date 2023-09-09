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

from . import globa
from . import er

class Environment():
    def __init__(self, host, port, username, env, encoding, deploy_path='', identity_file='', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.identity_file = identity_file
        self.password = password
        self.env = env
        self.encoding = encoding
        self._deploy_path = deploy_path
    def set_deploy_path(self, path):
        self._deploy_path = path
    def get_deploy_path(self):
        if not self._deploy_path:
            if globa.conf.project_name():
                return '/srv/drops/' + globa.conf.project_name()
            else:
                raise er.NoProjectNameOrDeploymentSet
        return self._deploy_path
    def to_conf(self):
        data = {
            'host':self.host,
            'port':self.port,
            'username':self.username,
            'encoding':self.encoding
            }
        if self._deploy_path:
            data['deploy_path'] = self._deploy_path
        if self.password:
            data['password'] = self.password
        if self.identity_file:
            data['identity_file'] = self.identity_file
        return data
    def __str__(self) -> str:
        return str({'host':self.host, 'port':self.port, 'username':self.username, 'identity_file':self.identity_file, 'password':'*', 'env':self.env, 'encoding':self.encoding, 'deploy_path':self._deploy_path})

class Conf():
    # 封装配置文件
    def __init__(self):
        self._data={
            'env':{}
        }

    def open(self, path=None):
        if not path:
            path = globa.args.config
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
        # 自动获取参数和配置文件内容
        if name == 'env':
            return {k:Environment(i) for k, i in  self._data['env'].items()}
        return self._data[name].copy()

    def set_project_name(self, n):
        # 设置项目名
        p = self._data.get('project', {})
        p['name'] = n
        self._data['project'] = p
        return self

    def save(self, path=None):
        if not path:
            path = self.path
        with open(path, 'w') as fd:
            fd.write(yaml.dump(self._data))
        return self

    def new(self, path, name):
        if os.path.isfile(path):
            raise er.ConfigFileAlreadyExists
        self._data = {'env': {
                'dev':{
                    'host':'example.org',
                    'port':'22',
                    'username':'root',
                    'password':'123456',
                    'identity_file':'~/.ssh/id_ed25519',
                    'encoding':'utf-8',
                    'deploy_path':'/srv/drops/'+name,
                }
            },
            'project':{
                'name': name,
            },
        }
        self.save(path)
        return self

    def set_env(self, name, env:Environment):
        self._data['env'][name] = env.to_conf()
        return self
    def remove_env(self, name):
        del(self._data['env'][name])
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
        if host is None:
            self.print_env(self._data['env'])
            return self

        self.print_host(host, self._data['env'][host])
        return self

    def has_env(self, name) -> bool:
        return name in self._data.get('env', {})

    def get_env(self, name) -> Environment:
        # 获取单个 env
        if name in self._data.get('env', {}):
            return Environment(env=name, **self._data['env'][name])
        raise er.EnvDoesNotExist(name)

    def project_name(self):
        return self._data.get('project', {}).get('name', "")
    # def has_default_env(self):
    #     return self._data.get('project', {}).get('default_env', False) and True
    # def get_default_env(self)->str:
    #     default_env = self._data.get('project', {}).get('default_env', None)
    #     if default_env:
    #         return self.get_env(default_env)
    #     raise er.NoDefaultEnvironmentIsSet