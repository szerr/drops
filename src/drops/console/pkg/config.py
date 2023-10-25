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

ENV_TYPE_REMOVE = 'remote'
ENV_TYPE_LOCAL = 'local'


class Environment():
    # env 环境配置，存储 env 配置数据和远程路径拼接。
    def __init__(self, name, type, project_name, deploy_path=None, host='', port=22,
                 username='root', encoding='utf-8', identity_file='', password=''):
        self.host = host
        self.port = port
        self.username = username
        self.identity_file = identity_file
        self.password = password
        self.encoding = encoding
        self.deploy_path = deploy_path
        self.name = name  # 动态赋值，不存在配置文件里
        self.project_name = project_name  # 动态赋值，不存在配置文件里
        if type in (ENV_TYPE_REMOVE, ENV_TYPE_LOCAL):
            self.type = type
        else:
            raise er.ArgsError('env can only be local or remote.')
        # 补全部署路径
        if not self.deploy_path:
            if self.type == ENV_TYPE_LOCAL:
                self.deploy_path = '.'
            else:
                self.deploy_path = self.join_path(
                    '/srv/drops/', self.project_name)

    def join_path(self, *p):
        p_li = []
        for i in p:
            p_li.append('/'.join([i for i in os.path.split(i) if i]))
        return '/'.join(p_li)

    def set_deploy_path(self, path):
        self.deploy_path = path

    def get_deploy_path(self, project_name=None):
        if not self.deploy_path:
            if project_name:
                return '/srv/drops/' + project_name
            else:
                raise er.NoProjectNameOrDeploymentSet
        return self.deploy_path

    def join_deploy_path(self, *p):
        return self.join_path(self.get_deploy_path(), *p)

    def docker_cmd_template(self, cmd):
        if self.type == ENV_TYPE_REMOVE:
            return 'cd ' + self.get_deploy_path() + ' && docker-compose %s' % cmd
        # 如果没有指定 env，在本地执行不需要 cd
        return 'docker-compose %s' % cmd

    def container_path(self):
        return self.get_deploy_path()

    def servers_path(self):
        return self.join_deploy_path('servers')

    def docker_compose_path(self):
        return self.join_deploy_path('docker-compose.yaml')

    def release_path(self):
        # 发布路径
        return self.join_deploy_path('release')

    def var_path(self):
        return self.join_deploy_path('var')

    def volumes_path(self):
        # volumes路径
        return self.join_deploy_path('volumes')

    # 用 / 结尾代表文件夹
    def container_path_dir(self):
        return self.get_deploy_path()+'/'

    def servers_path_dir(self):
        return self.join_deploy_path('servers', '')

    def release_path_dir(self):
        # 发布路径
        return self.join_deploy_path('release', '')

    def var_path_dir(self):
        return self.join_deploy_path('var', '')

    def volumes_path_dir(self):
        # volumes路径
        return self.join_deploy_path('volumes', '')

    def to_conf(self):
        data = {
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'encoding': self.encoding,
            'deploy_path': self.get_deploy_path(),
        }
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
             'password': '*', 'env': self.name, 'encoding': self.encoding, 'deploy_path': self.get_deploy_path(),
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


def gen_env_by_args(project_name, args):
    return Environment(host=args.host, port=args.port, username=args.username, name=args.env, encoding=args.encoding,
                       deploy_path=args.deploy_path, identity_file=args.identity_file, password=args.password,
                       type=args.env_type, project_name=project_name)


class Conf():
    # 封装配置文件
    def __init__(self):
        self._data = {
            'env': {}
        }
        self.work_path = os.getcwd()
        self.config_path = ''

    def open(self, config_path=None):
        if not config_path:
            config_path = globa.args.config

        self.work_path, _ = os.path.split(os.path.abspath(config_path))
        self.config_path = config_path

        with open(config_path) as fd:
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
            },
            'example': {
                'host': 'example.com',
                'port': 22,
                'username': 'root',
                'identity_file': '~/.ssh/id_ed25519',
                'password': '',
                'encoding': 'utf-8',
                'type': 'remote',
                'deploy_path': '/srv/drops/example',
            }
        },
            'project': {
                'name': name,
                'default_env': 'local',
        },
        }
        return self

    def set_env(self, env: Environment):
        if env.name:
            self._data['env'][env.name] = env.to_conf()
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
            # 如果没有设置部署路径，使用默认路径
            env_data = self._data['env'][name]
            # 低版本迁移提醒
            if not 'type' in env_data:
                raise er.ConfigurationFileFormatError(
                    self.config_path + " 中没有找到 type 字段，drops v1 配置中新增 type 字段，" +
                    "请参照文档对配置文件手动升级：" +
                    '''https://github.com/szerr/drops#%E9%85%8D%E7%BD%AE''')

            return Environment(name=name, project_name=self.project_name(), **env_data)
        raise er.EnvDoesNotExist(name)

    def project_name(self):
        pname = self._data.get('project', {}).get('name', "")
        if pname:
            return pname
        raise er.ProjectNameCannotBeEmpty

    def has_default_env(self):
        return self._data.get('project', {}).get('default_env', False) and True

    def get_default_env(self) -> Environment:
        default_env = self._data.get('project', {}).get('default_env', None)
        if default_env:
            return self.get_env(default_env)
        raise er.NoDefaultEnvironmentIsSet


_CONF_OBJ = None


def get_conf():
    global _CONF_OBJ
    if not _CONF_OBJ:
        _CONF_OBJ = Conf().open(globa.args.config)
    return _CONF_OBJ


def get_env() -> Environment:
    # 处理全局参数，读取配置文件，按优先级替换 env 参数
    conf = get_conf()
    if globa.args.env:
        if conf.has_env(globa.args.env):
            env = conf.get_env(globa.args.env)
        else:
            # 先设置 deploy_path 为空，后边会自动设置或报错。
            env = Environment(globa.args.env, ENV_TYPE_REMOVE,
                              deploy_path='', project_name=conf.project_name())
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
    if globa.args.env_type:
        env.type = globa.args.type
    if globa.args.deploy_path:
        env.deploy_path = globa.args.deploy_path
    return env
