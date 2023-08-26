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
        self.deploy_path = deploy_path
    def to_conf(self):
        data = {
            'host':self.host,
            'port':self.port,
            'username':self.username,
            'encoding':self.encoding
            }
        if self.deploy_path:
            data['deploy_path'] = self.deploy_path
        if self.password:
            data['password'] = self.password
        if self.identity_file:
            data['identity_file'] = self.identity_file
        return data
    def __str__(self) -> str:
        return str({'host':self.host, 'port':self.port, 'username':self.username, 'identity_file':self.identity_file, 'password':'*', 'env':self.env, 'encoding':self.encoding, 'deploy_path':self.deploy_path})

def gen_environment_by_arg(args):
    return Environment(host=args.host, port=args.port, username=args.username, identity_file=args.identity_file, password=args.password, env=args.env, encoding=args.encoding, deploy_path=args.deploy_path)


class Conf():
    # 封装配置文件
    def __init__(self):
        self._data=None

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
        if not self._data:
            self.open()
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
                    'deploy_path':'/srv/drops',
                }
            },
            'project':{
                'name': name
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
            return Environment(env=name, **self._data['env'][name])
        raise er.EnvDoesNotExist(name)

    def project_name(self):
        return self.open()._data['project']['name']

    def gen_env_by_arg(self):
        # 结合命令行参数和配置生成 env 对象
        env = gen_environment_by_arg(globa.args)
        # 如果参数制定了 env，取配置文件中的 env，按优先级做相应结合
        if globa.args.env:
            c = Conf().open()
            conf = c.get_env(env.env)
            # host 和 验证信息优先级高于配置文件
            if not env.host:
                env.host = conf.host
            if not env.identity_file and not env.password:
                if not env.identity_file and conf.identity_file:
                    env.identity_file = conf.identity_file
                else:
                    env.password = conf.password

            # 连接信息如果不是默认值，优先级高于配置文件
            if env.port == 22:
                env.port = conf.port
            if env.username == 'root':
                env.username = conf.username
            if env.encoding == 'utf-8':
                env.encoding = conf.encoding
            if env.deploy_path == '/srv/drops':
                env.deploy_path = conf.deploy_path
        return env
