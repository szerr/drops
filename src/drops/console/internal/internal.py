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
import shutil

from . import er
from . import ssh
from . import config
from . import globa

def work_path():
    # 当前 drops 项目绝对路径，drops.yaml 所在目录
    return os.getcwd()

def deploy_path():
    return globa.args.deploy_path

def volumes_path():
    # volumes路径
    return deploy_path() + '/' + config.Conf().project_name() + '/volumes/'

def container_path():
    # 容器路径，如果没有配置 env，始终返回当前目录
    if globa.args.env:
        return deploy_path() + '/' + config.Conf().project_name() + '/'
    return work_path()


def servers_path():
    return container_path() + 'servers/'


def docker_path():
    return container_path() + 'docker-compose.yaml'


def release_path():
    # 发布路径
    return container_path() + 'release/'


def var_path():
    return container_path() + 'var/'

def check_env_arg():
    # 检查 env 参数是否存在
    if not globa.args.env:
        raise er.ArgsError("The -e(--env) argument is required.")

def docker_cmd_template(cmd):
    # 执行 docker-compose 命令的模板
    if globa.args.env:
        return 'cd ' + container_path() + ' && docker-compose %s' % cmd
    # 如果没有指定 env，在本地执行不需要 cd 
    return 'docker-compose %s' % cmd


def ssh_template_key(key_path, port, username, host, b=''):
    # ssh 登录运行命令
    return 'ssh -p %d -i %s %s@%s "cd %s && %s"' % (port, key_path, username, host, container_path(), b)


def ssh_template_pwd(password, port, username, host, b=''):
    # ssh 登录运行命令
    return 'sshpass -p %s ssh -p %d %s@%s "cd %s && %s"' % (password, port, username, host, container_path(), b)


def rsync2remotely(env, src, target, exclude=[]):
    # rsync 本地同步到远程路径
    exclude = ' --exclude '.join(['', './.gitignore', './.git', './drops.yaml', './src', './secret'] + exclude)
    if env.identity_file:
        b = 'rsync -avzP --del -e "ssh -p {port} -i {key_path}" {exclude} {src} {username}@{host}:{target}'
        echo_b = b.format(
            src=src, target=target, key_path='<key_path>', port=env.port, username=env.username, host=env.host, exclude=exclude)
        b = b.format(
            src=src, target=target, key_path=env.identity_file, port=env.port, username=env.username, host=env.host, exclude=exclude)
    else:
        detection_cmd('sshpass')
        b = 'sshpass -p {password} rsync -avzP --del -e "ssh -p {port}" {exclude} {src} {username}@{host}:{target}'
        echo_b = b.format(
            src=src, target=target, password='<password>', port=env.port, username=env.username, host=env.host, exclude=exclude)
        b = b.format(
            src=src, target=target, password=env.password, port=env.port, username=env.username, host=env.host, exclude=exclude)
    print(echo_b)
    return system(b)


def rsync2local(env, src, target):
    # rsync 远程同步到本地
    if env.identity_file:
        b = 'rsync -avzP --del -e "ssh -p {port} -i %s" {username}@{host}:{src} {target}'.format(
            src=src, target=target, port=env.port, username=env.username, host=env.host)
        print(b%('<key_path>'))
        b = b % env.identity_file
    else:
        detection_cmd('sshpass')
        b = 'sshpass -p %s rsync -avzP --del -e "ssh -p {port}" {username}@{host}:{src} {target}'.format(
            src=src, target=target,  port=env.port, username=env.username, host=env.host)
        print(b%('<password>'))
        b = b % env.password
    return system(b)


def rsync2local_link_dest(env, src, target, link_dest):
    # rsync 远程同步到本地，设置链接
    if env.identity_file:
        b = 'rsync -avzP --del -e "ssh -p {port} -i %s" --link-dest={link_dest} {username}@{host}:{src} {target}'.format(
            src=src, target=target,  port=env.port, username=env.username, host=env.host, link_dest=link_dest)
        print(b)
        b = b % env.identity_file
    else:
        detection_cmd('sshpass')
        b = 'sshpass -p {%s} rsync -avzP --del -e "ssh -p {port}" --link-dest={link_dest} {username}@{host}:{src} {target}'.format(
            src=src, target=target,  port=env.port, username=env.username, host=env.host, link_dest=link_dest)
        print(b)
        b = b % env.password
    return system(b)


def Fatal(*e):
    print("Fatal!", *e)

# 多个命令会用到的参数
def add_container_arg(p):
    p.add_argument('container', type=str,
                   help="docker container name", nargs=1)

def add_arg_container(p):
    p.add_argument('container',
                   help="要执行操作的容器。", type=str, nargs='*')

def add_arg_force(p):
    p.add_argument("-f", '--force',
                   help="强制执行，不再提示确认。", default=False, action='store_true')

def detection_cmd(*bl):
    # 确认命令是否存在
    for b in bl:
        for p in os.environ['PATH'].split(':'):
            if os.path.isdir(p) and b in os.listdir(p):
                break
        else:
            raise er.CmdNotExist(b)
    return True

def system(b):
    # os.system 在不同平台的行为不同，特别在 linux 下，是一个 16 位数，如果直接返回给 shell，会被截取低 8 位。这里做平台兼容。
    exit_code = os.system(b)
    if exit_code:
        if exit_code > 255:
            exit_code = exit_code / 256
    return exit_code

def ssh_shell(env, b):
    detection_cmd('ssh')
    if env.identity_file:
        return system(ssh_template_key(
            env.identity_file, env.port, env.username, env.host, b))
    else:
        detection_cmd('sshpass')
        return system(ssh_template_pwd(
            env.password, env.port, env.username, env.host, b))


def rsync_release(env, force):
    print('------- sync release -------')
    detection_cmd('rsync')
    return rsync2remotely(env, 'release', container_path())


def rsync_docker(env, force=False):
    # 同步项目到远程目录
    print('------- sync docker-compose.yaml -------')
    detection_cmd('rsync')
    return rsync2remotely(env, 'docker-compose.yaml', docker_path())


def rsync_image(env, force):
    print('------- sync image -------')
    detection_cmd('rsync')
    return rsync2remotely(env, 'image', container_path())

def rsync_ops(env, force):
    print('------- sync ops -------')
    detection_cmd('rsync')
    exclude = [i for i in os.listdir(work_path()) if not i in ['docker-compose.yaml', 'docker-compose.yml', 'release', 'image']]
    return rsync2remotely(env, '.', container_path(), exclude)

def rsync_var(env, force):
    if not confirm_empty_dir(env, var_path()):
        if not force and not user_confirm("主机 %s 远程目录 %s 不是空目录，是否继续同步？" % (env.host, var_path())):
            raise er.UserCancel
    return rsync2remotely(env, 'var', container_path())


def rsync_volumes(env, force):
    if not confirm_empty_dir(env, volumes_path()):
        if not force and not user_confirm("主机 %s 远程目录 %s 不是空目录，是否继续同步？" % (env.host, volumes_path())):
            raise er.UserCancel
    return rsync2remotely(env, 'volumes', container_path())

def sync(env, force=False, obj='ops'):
    # rsync 不会创建上一层文件夹，同步前创建
    c = ssh.Client(env)
    if force: # rsync 只同步文件时，不会创建当前文件夹。在判断是否是 drops 项目时会自动创建，但是 --force 会绕过。在 -f 生效时直接创建文件夹。
        _, status = c.exec(' mkdir -p ' + container_path())
    else:
        _, status = c.exec(' mkdir -p ' + deploy_path())
        # if not confirm_drops_project(c):
        #     if not user_confirm("环境 %s 主机 %s 远程目录 %s 可能不是 drops 项目，继续同步可能会导致丢失数据。是否继续？" % (env.env, env.host, container_path())):
        #         raise er.UserCancel
    if status != 0:
        raise er.CmdExecutionError('mkdir -p ' + deploy_path() + ', code=' + str(status))
    arg = (env, force)
    if obj == 'ops':
        return rsync_ops(*arg)
    elif obj == 'docker':
        return rsync_docker(*arg)
    elif obj == 'release':
        return rsync_release(*arg)
    elif obj == 'image':
        return rsync_image(*arg)
    elif obj == 'var':
        return rsync_var(*arg)
    elif obj == 'volumes':
        return rsync_volumes(*arg)
    else:
        raise er.UnsupportedSyncObject(obj)


def rsync_backup(env, src, target, link_desc=''):
    detection_cmd('rsync')
    if link_desc:
        return rsync2local_link_dest(env, src, target, link_desc)
    return rsync2local(env, src, target)


def backup(env, obj, target, time_format='%Y-%m-%d_%H:%M:%S', link_desc='', keep=-1, cod=False, force=False):
    backup2dir = target
    link_dir = link_desc
    if cod:  # 创建项目名的文件夹
        backup2dir = os.path.join(backup2dir, config.Conf().project_name())
    # 如果设定了时间格式
    if time_format:
        # 备份目录是备份对象下的时间目录
        backup2dir = os.path.join(backup2dir, '{obj}')
        # 如果设置了 link_desc
    # 需要备份的目录列表
    srcLi = []
    if obj == 'all':
        srcLi = [
            [release_path(), backup2dir.format(obj='release')],
            [servers_path(), backup2dir.format(obj='servers')],
            [var_path(), backup2dir.format(obj='var')],
            [volumes_path(), backup2dir.format(obj='volumes')],
            [docker_path(), backup2dir.format(obj='docker-compose.yaml')],
        ]
    elif obj == 'ops':
        srcLi = [
            [release_path(), backup2dir.format(obj='release')],
            [servers_path(), backup2dir.format(obj='servers')],
            [docker_path(), backup2dir.format(obj='docker-compose.yaml')],
        ]
    elif obj == 'docker':
        srcLi = [
            [docker_path(), backup2dir.format(obj='docker-compose.yaml')],
        ]
    elif obj == 'release':
        srcLi = [
            [release_path(), backup2dir.format(obj='release')],
        ]
    elif obj == 'servers':
        srcLi = [
            [servers_path(), backup2dir.format(obj='servers')],
        ]
    elif obj == 'var':
        srcLi = [
            [var_path(), backup2dir.format(obj='var')],
        ]
    elif obj == 'volumes':
        srcLi = [
            [volumes_path(), backup2dir.format(obj='volumes')],
        ]
    else:
        raise er.UnsupportedBackupObject(obj)

    for s in srcLi:
        to_path = s[1]
        if not os.path.isdir(s[1]):
            os.mkdir(s[1])
        if not link_desc:
            # 组装 link_desc
            lsdir = []
            # 排除不符合 format 的目录
            for i in os.listdir(s[1]):
                try:
                    time.strptime(i, time_format)
                    lsdir.append(i)
                except ValueError:
                    pass
            if not lsdir:
                print("%s 路径下没有找到符合 %s 的文件夹，--link-dest 功能关闭。" %
                      (s[1], time_format))
            # 备份文件夹的时间命名
            tar_time = time.strftime(
                time_format, time.localtime(time.time()))
            if tar_time in lsdir:
                lsdir.remove(tar_time)  # 排除掉本次要备份的文件夹
            if lsdir:
                lsdir.sort(reverse=True)
                # link 目录是排序后最大的目录
                link_dir = lsdir[0]
                link_desc = os.path.join(work_path(), s[1], link_dir)
                if keep > 0:
                    # 本次新增的备份也算一个
                    rm_dir = lsdir[keep-1:]
                    for r in rm_dir:
                        rd = os.path.join(s[1], r)
                        print('delete:', rd)
                        # docker-compose.yaml 是文件，其他是目录
                        if os.path.isdir(rd):
                            shutil.rmtree(rd)
                        else:
                            os.remove(rd)
                    if keep == 1:
                        link_desc = ''
            to_path = os.path.join(s[1], tar_time)
        if not force and os.path.isdir(to_path) and os.listdir(to_path):
            if not user_confirm("本地目录 %s 已存在且非空，继续同步可能会导致文件丢失，是否继续同步？" % (to_path)):
                raise er.UserCancel
        rsync_backup(env, s[0], to_path, link_desc)


def docker_compose_cmd(cmd, host):
    # docker_compose_cmd 解析命令行参数，只需要 ssh 部分的参数。
    # 接收一个字符串模板，
    # 拼接进入工作目录的命令，传入 cmd 并返回。
    # 可以执行任意 docker-compose 命令。
    for i in ('&', '`', '"', "'", ';'):  # 防止执行其他什么东西
        if i in cmd:
            raise er.CmdCannotContain(i)
    return exec(docker_cmd_template(cmd), host)


def exec(cmd, env):
    # 对 env 执行任意命令, 如果没有设置 env，在当前目录执行。
    if not env.env:
        print('run local:', cmd)
        return system(cmd)
    print('run host: ', env.env, cmd)
    c = ssh.Client(env)
    # 在远程路径下执行，要 cd 到项目目录
    stdout, status = c.exec(cmd)
    if status != 0:
        print('----------------- fail -----------------')
        print(stdout, status)
        raise er.CmdExecutionError(cmd + ', code=' + str(status))
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


def confirm_drops_project(client):
    # 防止出现同步时误删除，同步前检查目录。目录存在返回0，否则返回1
    while True:
        _, s = client.exec(
            '''if [ -d %s ]; then exit 0; else exit 1; fi''' % container_path(), False)
        if s != -1:
            break
    # 目录不存在时可以安全同步，创建项目目录
    if s == 1:
        client.exec('''mkdir -p ''' + container_path(), False)
        return True

    b = '''if [ -f %s ] && [ -d %s ]; then exit 0; else exit 1; fi''' % (
        container_path()+'/docker-compose.yaml', container_path()+'/servers')

    while True:
        _, s = client.exec(b, False)
        # 这条命令很容易返回 -1，貌似是 paramiko 的锅。重试。
        if s != -1:
            break
    # 目录存在，却没有 docker-compose 或 servers，可能不是 drops 项目
    if s == 0:
        return True
    return False


def confirm_empty_dir(env, path):
    # 返回 path 是否是空目录
    c = ssh.Client(env)
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

def command_exists(b)->bool:
    for cmdpath in os.environ['PATH'].split(':'):
        if os.path.isdir(cmdpath) and b in os.listdir(cmdpath):
            return True
    return False
        