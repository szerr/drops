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

ENV_REMOTE = 'remote'
ENV_LOCAL = 'local'


def join_path(*p):
    # 用 `/` 字符连接路径
    p_li = []
    for i in p:
        p_li.append('/'.join([i for i in os.path.split(i) if i]))
    return '/'.join(p_li)


class Environment():
    def __init__(self, env, type, host='', port='', username='', encoding='',
                 deploy_path='', identity_file='', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.identity_file = identity_file
        self.password = password
        self.env = env
        self.encoding = encoding
        self.deploy_path = deploy_path
        if type in (ENV_REMOTE, ENV_LOCAL):
            self.type = type
        else:
            raise er.ArgsError('env can only be %s or %s.' %
                               (ENV_REMOTE, ENV_LOCAL))

    def to_conf(self):
        data = {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'encoding': self.encoding
        }
        if self.deploy_path:
            data['deploy_path'] = self.deploy_path
        if self.password:
            data['password'] = self.password
        if self.identity_file:
            data['identity_file'] = self.identity_file
        if self.type in ('remote', 'local'):
            data['type'] = self.type
        else:
            raise er.ArgsError('env can only be local or remote.', self.type)
        return data

    def __str__(self) -> str:
        return str(
            {'host': self.host, 'port': self.port, 'username': self.username, 'identity_file': self.identity_file,
             'password': '*', 'env': self.env, 'encoding': self.encoding, 'deploy_path': self.deploy_path,
             'type': self.type})

    def path_join(self, *p):
        # 用 `/` 字符连接路径
        sep = '/'

        # 去掉所有分隔符
        p_li = [i for l in p for i in l.split(sep) if i]

        start = ''
        end = ''
        if p[0].startswith(sep):
            start = sep
        if not p[-1] or p[-1].endswith(sep):
            end = sep
        return start + sep.join(p_li) + end

    def container_path(self):
        return self.deploy_path

    def servers_path(self):
        return self.deploy_path + '/servers'

    def docker_compose_path(self):
        return self.deploy_path + '/docker-compose.yaml'

    def release_path(self):
        # 发布路径
        return self.deploy_path + '/release'

    def volumes_path(self):
        # volumes路径
        return self.deploy_path + '/volumes'

    def var_path(self):
        return self.deploy_path + '/var'

    def docker_cmd_template(self, cmd):
        # 执行 docker-compose 命令的模板
        return 'cd ' + self.container_path() + ' && docker-compose %s' % cmd


def gen_env_by_args(args):
    return Environment(host=args.host, port=args.port, username=args.username, env=args.env, encoding=args.encoding,
                       deploy_path=args.deploy_path, identity_file=args.identity_file, password=args.password,
                       type=args.env_type)


class Conf():
    # 封装配置文件
    def __init__(self):
        self._data = {
            'env': {}
        }
        self.work_path = os.getcwd()

    def open(self, path=None):
        if not path:
            path = globa.args.config
        self.work_path, _ = os.path.split(path)
        with open(path) as fd:
            c = yaml.load(fd.read(), Loader=yaml.Loader)
        if 'project' not in c:
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
        print(self._data['env'])
        if name == 'env':
            return {k: Environment(k, **i) for k, i in self._data['env'].items()}
        return self._data[name].copy()

    def set_project_name(self, n):
        # 设置项目名
        p = self._data.get('project', {})
        p['name'] = n
        self._data['project'] = p
        return self

    def save(self, path=None):
        if not path:
            path = globa.args.config
        with open(path, 'w') as fd:
            fd.write(yaml.dump(self._data))
        return self

    def init_template(self, name):
        self._data = {'env': {
            'local': {
                'deploy_path': '.',
                'type': 'local',
            }
        },
            'project': {
                'name': name,
                'default_env': 'local',
        },
        }
        return self

    def set_env(self, env: Environment):
        if env.env:
            self._data['env'][env.env] = env.to_conf()
            return self
        else:
            raise er.ArgsError('env name')

    def remove_env(self, name):
        del (self._data['env'][name])
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
            self.print_host(h, item, head + '  ')

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

    def has_default_env(self):
        return self._data.get('project', {}).get('default_env', False) and True

    def get_default_env(self) -> Environment:
        default_env = self._data.get('project', {}).get('default_env', None)
        if default_env:
            return self.get_env(default_env)
        raise er.NoDefaultEnvironmentIsSet


def get_env():
    # 处理全局参数，读取配置文件，按优先级替换 env 参数
    conf = Conf().open(globa.args.config)
    if globa.args.env:
        if conf.has_env(globa.args.env):
            env = conf.get_env(globa.args.env)
        else:
            env = Environment(globa.args.env, ENV_REMOTE)  # 默认 env 类型是远程
    elif conf.has_default_env():
        env = conf.get_default_env()
    else:
        raise er.NoDefaultEnvironmentIsSet

    # 有传参时替换掉对应的 env 属性。参数优先级高于配置文件。
    if globa.args.host:
        env.host = globa.args.host
    if globa.args.port:
        env.port = globa.args.port
    if globa.args.username:
        env.username = globa.args.username
    if globa.args.identity_file:
        env.identity_file = globa.args.identity_file
    if globa.args.password:
        env.password = globa.args.password
    if globa.args.encoding:
        env.encoding = globa.args.encoding
    if globa.args.deploy_path:
        env.deploy_path = globa.args.deploy_path
    if globa.args.env_type:
        env.type = globa.args.type
    return env
