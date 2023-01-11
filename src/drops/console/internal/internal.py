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


import os
import time

from . import er
from . import ssh
from . import config

port = 22  # 默认端口


def volumes_path():
    # volumes路径
    return '/srv/drops/%s/volumes/' % config.Conf().getProjectName()


def container_path():
    # 容器路径
    return '/srv/drops/%s/' % config.Conf().getProjectName()


def servers_path():
    return '/srv/drops/%s/servers/' % config.Conf().getProjectName()


def docker_path():
    return container_path() + 'docker-compose.yaml'


def release_path():
    # 发布路径
    return '/srv/drops/%s/release/' % config.Conf().getProjectName()


def var_path():
    return '/srv/drops/%s/var/' % config.Conf().getProjectName()


def docker_cmd_template(cmd):
    # 执行 docker-compose 命令的模板，看起来像是这样：
    #  cd <container_path> && docker-compose %s"
    return 'cd ' + container_path() + ' && docker-compose %s' % cmd


def ssh_template_key(key_path, port, username, host, b=''):
    # ssh 登录运行命令
    return 'ssh -p %d -i %s %s@%s "cd %s && %s"' % (port, key_path, username, host, container_path(), b)


def ssh_template_pwd(password, port, username, host, b=''):
    # ssh 登录运行命令
    return 'sshpass -p %s ssh -p %d %s@%s "cd %s && %s"' % (password, port, username, host, container_path(), b)


def rsync2remotely(host, src, target):
    # rsync 本地同步到远程路径
    if host.key:
        os.system('rsync -avzP --del -e "ssh -p {port} -i {key_path}" --exclude "drops.yaml" --exclude ".git" --exclude ".gitignore" {src} {username}@{host}:{target}'.format(
            src=src, target=target, key_path=host.key, port=host.port, username=host.username, host=host.host))
    else:
        detection_cmd('sshpass')
        os.system('sshpass -p {password} rsync -avzP --del -e "ssh -p {port}" --exclude "drops.yaml" --exclude ".git" --exclude ".gitignore" {src} {username}@{host}:{target}'.format(
            src=src, target=target, password=host.password, port=host.port, username=host.username, host=host.host))


def rsync2local(host, src, target):
    # rsync 远程同步到本地
    if host.key:
        os.system('rsync -avzP --del -e "ssh -p {port} -i {key_path}" --exclude "drops.yaml" --exclude ".git" --exclude ".gitignore" {username}@{host}:{src} {target}'.format(
            src=src, target=target, key_path=host.key, port=host.port, username=host.username, host=host.host))
    else:
        detection_cmd('sshpass')
        os.system('sshpass -p {password} rsync -avzP --del -e "ssh -p {port}" --exclude "drops.yaml" --exclude ".git" --exclude ".gitignore" {username}@{host}:{src} {target}'.format(
            src=src, target=target, password=host.password, port=host.port, username=host.username, host=host.host))


def Fatal(*e):
    print("Fatal!", *e)


def add_ssh_arg(p):
    p.add_argument('-h', type=str, help='host', required=False)
    p.add_argument('-p', '--port', dest='port', type=int,
                   help="ssh port", default=22)


def add_container_arg(p):
    p.add_argument('container', type=str,
                   help="docker container name", nargs=1)


def add_arg_container(p):
    p.add_argument('container',
                   help="要执行操作的容器。", type=str, nargs='*')


def add_arg_force(p):
    p.add_argument("-f", '--force',
                   help="强制执行，不再提示确认。", default=False, action='store_true')


def add_arg_group(p):
    p.add_argument("-g", "--group",
                   help="要执行操作的主机组，默认 test。", type=str, default='test')


def get_arg_group_from_conf(p):
    return config.Conf().get_group(p.group)


def add_arg_group_host(p):
    add_arg_group(p)
    p.add_argument('--hosts',
                   help="要执行操作的主机。", type=str, nargs='*')


def get_arg_group_host_from_conf(p):
    return config.Conf().get_hosts(p.group, p.hosts)


def parse_args(p):
    return p.parse_args()


def detection_cmd(*bl):
    # 确认命令是否存在
    for b in bl:
        for p in os.environ['PATH'].split(':'):
            if os.path.isdir(p) and b in os.listdir(p):
                break
        else:
            raise er.CmdNotExist(b)
    return True


def ssh_shell(hosts, b):
    detection_cmd('ssh')
    for host in hosts.values():
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + release_path())
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + release_path())
        if host.key:
            os.system(ssh_template_key(
                host.key, host.port, host.username, host.host, b))
        else:
            detection_cmd('sshpass')
            os.system(ssh_template_pwd(
                host.password, host.port, host.username, host.host, b))


def rsync_release(hosts, force):
    print('------- sync release -------')
    detection_cmd('rsync')
    for host in hosts.values():
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + release_path())
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + release_path())
        # TODO 0.2.1 添加向下兼容
        if not os.path.isdir('release'):
            os.mkdir('release')
        rsync2remotely(host, 'release/', release_path())


def rsync_docker(hosts, force=False):
    # 同步项目到远程目录
    print('------- sync docker-compose.yaml -------')
    detection_cmd('rsync')
    for host in hosts.values():
        if not force and not confirm_drops_project(host):
            if not user_confirm("主机 %s 远程目录可能不是 drops 项目，是否继续同步？" % host.host):
                raise er.UserCancel
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + container_path())
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + container_path())
        rsync2remotely(host, 'docker-compose.yaml', docker_path())


def rsync_servers(hosts, force):
    print('------- sync servers -------')
    detection_cmd('rsync')
    for host in hosts.values():
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + servers_path())
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + servers_path())
        rsync2remotely(host, 'servers/', servers_path())


def rsync_var(hosts, force):
    for host in hosts.values():
        if not confirm_empty_dir(host, var_path()):
            if not force and not user_confirm("主机 %s 远程目录 %s 不是空目录，是否继续同步？" % (host.host, var_path())):
                raise er.UserCancel
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + var_path())
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + var_path())
        rsync2remotely(host, 'var/', var_path())


def rsync_volumes(hosts, force):
    for host in hosts.values():
        if not confirm_empty_dir(host, volumes_path()):
            if not force and not user_confirm("主机 %s 远程目录 %s 不是空目录，是否继续同步？" % (host.host, volumes_path())):
                raise er.UserCancel
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + volumes_path())
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + volumes_path())
        rsync2remotely(host, 'volumes/', volumes_path())


def sync(hosts, force=False, obj='ops'):
    arg = (hosts, force)
    if obj == 'ops':
        rsync_docker(*arg)
        rsync_release(*arg)
        rsync_servers(*arg)
    elif obj == 'docker':
        rsync_docker(*arg)
    elif obj == 'release':
        rsync_release(*arg)
    elif obj == 'servers':
        rsync_servers(*arg)
    elif obj == 'var':
        rsync_var(*arg)
    elif obj == 'volumes':
        rsync_volumes(*arg)
    else:
        raise er.UnsupportedSyncObject(obj)


def docker_compose_cmd(cmd, hosts):
    # docker_compose_cmd 解析命令行参数，只需要 ssh 部分的参数。
    # 接收一个字符串模板，
    # 拼接进入工作目录的命令，传入 cmd 并返回。
    # 可以执行任意 docker-compose 命令。
    for i in ('&', '`', '"', "'", ';'):  # 防止执行其他什么东西
        if i in cmd:
            raise er.CmdCannotContain(i)
    return exec(docker_cmd_template(cmd), hosts)


def exec(cmd, hosts):
    # 对 host 执行任意远程命令
    result = {}
    for host in hosts.values():
        print('run host: ', host.host)
        c = ssh.Client(**host.to_conf())
        stdout, status = c.exec(cmd)
        if status != 0:
            result[host.host] = [stdout, status]

    if result:
        print('----------------- fail -----------------')
        for k, i in result.items():
            print('host:', k)
            print(i[0], i[1])
        raise er.CmdExecutionError(cmd)
    return 0


def user_confirm(*l):
    s = ' '.join(l)
    for _ in range(3):
        try:
            a = input(s + '[y/N]')
        except KeyboardInterrupt:
            return False
        if a == 'y':
            return True
        elif a in ['n', 'N']:
            return False
    return False


def confirm_drops_project(host):
    # 防止出现同步时误删除，同步前检查目录。
    c = ssh.Client(**host.to_conf())

    # 目录存在返回0，否则返回1
    while True:
        _, s = c.exec(
            '''if [ -d %s ]; then exit 0; else exit 1; fi''' % container_path(), False)
        if s != -1:
            break
    # 目录不存在时可以安全同步
    if s == 1:
        return True
    b = '''if [ -f %s ] && [ -d %s ]; then exit 0; else exit 1; fi''' % (
        container_path()+'/docker-compose.yaml', container_path()+'/servers')

    while True:
        _, s = c.exec(b, False)
        # 这条命令很容易返回 -1，貌似是 paramiko 的锅。重试。
        if s != -1:
            break
    # 目录存在，却没有 docker-compose 或 servers，可能不是 drops 项目
    if s == 0:
        return True
    return False


def confirm_empty_dir(host, path):
    # 返回 path 是否是空目录
    c = ssh.Client(**host.to_conf())
    # 目录存在返回0，否则返回1
    while True:
        _, s = c.exec(
            '''if [ -d %s ]; then exit 0; else exit 1; fi''' % path, False)
        if s != -1:
            break
    # 目录不存在时可以安全同步
    if s == 1:
        return True
    # 空目录返回 0， 否则返回 1
    while True:
        _, s = c.exec(
            '''if [ "$(ls -A %s)" ]; then exit 1; else exit 0 ; fi''' % path, False)
        if s != -1:
            break

    if s == 0:
        return True
    return False
