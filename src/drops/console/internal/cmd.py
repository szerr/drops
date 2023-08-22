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
import shutil

import drops
from . import config
from . import internal

def add_new_cmd(s):
    p = s.add_parser(
        'new', help='Create a drops project.')
    p.add_argument("dirName",  type=str, help="目录名，如果没有项目名会作为默认项目名。")
    p.add_argument("projectName",  type=str,
                   help="项目名。", default='', nargs='?')
    p.set_defaults(func=new_cmd)


def new_cmd(arg):
    if arg.dirName in os.listdir(os.getcwd()):
        internal.Fatal("File exists: ", os.path.join(os.getcwd(), arg.dirName))
        return
    objPath = drops.__path__[0]
    shutil.copytree(os.path.join(objPath, 'docker_ops'),
                    os.path.join(os.getcwd(), arg.dirName))
    os.chdir(arg.dirName)
    c = config.Conf().open()
    if arg.projectName:
        c.set_project_name(arg.projectName)
    else:
        c.set_project_name(arg.dirName)
    c.save()

def add_backup_cmd(s):
    p = s.add_parser(
        'backup', help='基于 rsync --del --link-dest 的增量备份。更改参数前先测试，以免写错删掉已有的备份文件。')
    internal.add_arg_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=backup_cmd)
    p.add_argument('obj', type=str, default='volumes', choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'ops', 'all'], nargs='?',
        help='''同步的文件夹。docker: docker-compose，ops 是除 var 和 volumes 的所有。''')
    p.add_argument('-t', '--target',
                   help="目标路径", default='backup/')
    p.add_argument('-d', '--time-format', default='%Y-%m-%d_%H:%M:%S',
                   help='目标路径下创建文件夹名的时间模板，与 python time.strftime format 参数相同。如 %%Y-%%m-%%d_%%H:%%M:%%S')
    p.add_argument('-l', '--link-dest',
                   help='未更改时链接到指定文件夹。默认是备份路径中符合 format 排序后最大的文件夹。')
    p.add_argument('-k', '--keep',
                   type=int, help="保留的备份个数，只有 format 开启时启用。本次备份也算一个。-1 保留所有。", default='-1')
    p.add_argument("-c", '--cod',
                   help="在目标路径创建项目名命名的文件夹", default=False, action='store_true')


def backup_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    if not os.path.isdir(p.target):
        os.mkdir(p.target)
    return internal.backup(host,  p.obj, p.target, p.time_format, p.link_dest, p.keep, p.cod, p.force)

def add_deploy_https_cert_cmd(s):
    p = s.add_parser(
        'deploy-https-cert', help='申请并部署 https 证书，基于 acme.sh。')
    internal.add_arg_host(p)
    p.add_argument("-f", '--force',
                   help="重新申请证书。", default=False, action='store_true')
    p.set_defaults(func=deploy_https_cert_cmd)


def deploy_https_cert_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'exec -T acme.sh redeploy-ssl'
    if p.force:
        b += ' --force'
    # redeploy-ssl 是作为文件映射进去的，需要重启才会更新。
    internal.docker_compose_cmd('restart acme.sh', host)
    print("开始申请证书，如果出现文件复制失败，请确认 nginx 容器是否正常运行。")
    print("如果域名没有变动，acme.sh 不会重新申请证书。--force 强制重新申请证书。")
    return internal.docker_compose_cmd(b, host)

def add_deploy_cmd(s):
    p = s.add_parser(
        'deploy', help='部署并启动服务。')
    internal.add_arg_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=deploy_cmd)


def deploy_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    internal.sync(host, p.force)
    return internal.docker_compose_cmd("up -d", host)

def add_echo_paths_cmd(s):
    p = s.add_parser(
        'echo-paths', help='显示 drops 用到的各部署路径')
    p.set_defaults(func=deploy_echo_paths_cmd)


def deploy_echo_paths_cmd(p):
    print('容器路径，docker-compose.yaml 所在文件夹:', internal.container_path())
    print('发布路径，应用程序文件夹:', internal.release_path())
    print('volumes 路径，应用程序数据文件夹:', internal.volumes_path())

def add_exec_cmd(s):
    p = s.add_parser(
        'exec', help='在任意容器中执行命令。')
    p.add_argument("container", metavar="container",
                   type=str, help="容器名")
    internal.add_arg_host(p)
    p.add_argument('cmds',
                   help="要执行的命令。", type=str, nargs='+')
    p.set_defaults(func=exec_cmd)


def exec_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    internal.exec(internal.docker_cmd_template(
        "exec -T "+p.container + ' ' + ' '.join(p.cmds)), host)

def host_cmd(a):
    if a.cmd == 'add' or a.cmd == 'change':
        if a.host_alias == None:
            raise er.ArgsError('至少需要传入 host-alias 参数')
        if a.host == None:
            raise er.ArgsError('至少需要传入 host 参数')
        c = {'host': a.host, 'port': a.port,
             'username': a.username, 'coding': a.coding, 'host-alias': a.host_alias}
        if a.password is not None:
            c['password'] = a.password
        elif a.key is not None:
            c['key'] = a.key
        else:
            raise er.ArgsError('密码或者 key 至少要传入一个。')
        if a.cmd == 'change':
            config.Conf().change_host(**c)
        else:
            config.Conf().add_host(**c)

    elif a.cmd == 'remove':
        if a.host_alias == None:
            raise er.ArgsError('至少需要传入 host-alias 参数')
        config.Conf().remove_host(a.host_alias)
    elif a.cmd == 'ls':
        config.Conf().ls()
    else:
        config.Conf().ls()


def add_host_cmd(s):
    p = s.add_parser(
        'host', help='管理 drops 部署主机。因为密码是明文存储的，强烈建议用 key 做验证。')
    p.add_argument('cmd', type=str, choices=[
                   'ls', 'add', 'remove', 'change'], nargs='?', help="default ls")
    p.add_argument("--host-alias", metavar="default",
                   type=str, help="host 类型，比方说 default、test、dev、online。default 是关键字，所有命令不指定 --host-alias 的话默认对 default 进行操作。")
    p.add_argument("host", metavar="ssh.example.com",
                   type=str, help="host.", default=None, nargs='?')
    p.add_argument("port", metavar="22",
                   type=int, help="ssh port.", default=22, nargs='?')
    p.add_argument("username", metavar="root",
                   type=str, help="ssh username.", default='root', nargs='?')
    p.add_argument('coding', metavar="coding",
                   type=str, help="shell coding, default is utf-8.", default='utf-8', nargs='?')
    p.add_argument("-p", '--password',
                   type=str, help="ssh password. Note that the password is stored in plain text, and key verification is strongly recommended.", default=None)
    p.add_argument("-k", '--key', metavar="~/.ssh/id_ed25519",
                   type=str, help="ssh key path", default=None)
    p.set_defaults(func=host_cmd)

def add_init_env_debian_cmd(s):
    p = s.add_parser(
        'init-debian-env', help='初始化 debian 系远程环境。')
    internal.add_arg_host(p)
    p.set_defaults(func=init_env_debian_cmd)


def init_env_debian_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    bin = 'apt-get update && apt-get install -y rsync docker-compose'
    internal.exec(bin, host)

def add_init_cmd(s):
    p = s.add_parser(
        'init', help='在当前目录初始化项目。')
    p.set_defaults(func=new_init)
    p.add_argument("projectName", metavar="projectName",
                   type=str, help="项目名。", nargs='?')


def new_init(p):
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    pwd = os.getcwd()
    if p.projectName == None:
        p.projectName = os.path.split(pwd)[-1]

    for i in os.listdir(objPath):
        s = os.path.join(objPath, i)
        t = os.path.join(pwd, i)
        if os.path.isdir(s):
            shutil.copytree(s, t)
        else:
            shutil.copyfile(s, t)

    c = Conf()
    c.setProjectName(p.projectName)

def add_kill_cmd(s):
    p = s.add_parser(
        'kill', help='杀掉容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    p.set_defaults(func=kill_cmd)


def kill_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'kill'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, host)

def add_logs_cmd(s):
    p = s.add_parser(
        'logs', help='输出容器日志。')
    p.add_argument("container", metavar="container",
                   type=str, help="容器名")
    p.add_argument("-f", '--follow',
                   help="持续日志输出。", default=False, action='store_true')
    internal.add_arg_host(p)
    p.set_defaults(func=logs_cmd)


def logs_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'logs '
    if p.follow:
        b += '-f '
    return internal.docker_compose_cmd(b+p.container, host)


def add_new_cmd(s):
    p = s.add_parser(
        'new', help='Create a drops project.')
    p.add_argument("dirName",  type=str, help="目录名，如果没有项目名会作为默认项目名。")
    p.add_argument("projectName",  type=str,
                   help="项目名。", default='', nargs='?')
    p.set_defaults(func=new_cmd)


def new_cmd(arg):
    from . import config
    from . import internal

    if arg.dirName in os.listdir(os.getcwd()):
        internal.Fatal("File exists: ", os.path.join(os.getcwd(), arg.dirName))
        return
    objPath = drops.__path__[0]
    shutil.copytree(os.path.join(objPath, 'docker_ops'),
                    os.path.join(os.getcwd(), arg.dirName))
    os.chdir(arg.dirName)
    c = config.Conf().open()
    if arg.projectName:
        c.set_project_name(arg.projectName)
    else:
        c.set_project_name(arg.dirName)
    c.save()

def add_nginx_force_reload_cmd(s):
    p = s.add_parser(
        'nginx-force-reload', help="重载 nginx 配置，会重载证书。")
    internal.add_arg_host(p)
    p.set_defaults(func=nginx_force_reload_cmd)


def nginx_force_reload_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    internal.exec(internal.docker_cmd_template(
        "exec -T nginx nginx -g 'daemon on; master_process on;' -s reload"), host)

def add_nginx_reload_cmd(s):
    p = s.add_parser(
        'nginx-reload', help='重载 nginx 配置，不会重载证书。')
    internal.add_arg_host(p)
    p.set_defaults(func=nginx_reload_cmd)


def nginx_reload_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    return internal.docker_compose_cmd('exec -T nginx nginx -s reload', host)

def add_project_cmd(s):
    p = s.add_parser(
        'project', help='项目信息')
    p.set_defaults(func=project_cmd)

    subparsers = p.add_subparsers(metavar="")
    n = subparsers.add_parser('name')
    n.add_argument('name', help="传入参数设置项目名，没有参数输出项目名",
                   type=str, nargs='?', default=None)


def project_cmd(p):
    c = config.Conf().open()
    if 'name' in p:
        if p.name == None:
            print(c.get_project_name())
        else:
            c.set_project_name(p.name)
    else:
        for k, i in c._data['project'].items():
            print(k, ': ', i, sep='')

def add_ps_cmd(s):
    p = s.add_parser(
        'ps', help='输出正在运行的容器。')
    internal.add_arg_host(p)
    p.set_defaults(func=ps_cmd)


def ps_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    return internal.docker_compose_cmd("ps", host)


def add_pull_cmd(s):
    p = s.add_parser(
        'pull', help='拉取容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    p.set_defaults(func=pull_cmd)


def pull_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'pull'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, host)


def add_redeploy_cmd(s):
    p = s.add_parser(
        'redeploy', help='部署并启动服务，重新编译容器，移除不再用的容器。')
    internal.add_arg_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=redeploy_cmd)


def redeploy_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    internal.sync(host, p.force)
    return internal.docker_compose_cmd("up -d --build --remove-orphans", host)

def add_restart_cmd(s):
    p = s.add_parser(
        'restart', help='重启容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    p.set_defaults(func=restart_cmd)


def restart_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'restart'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, host)

def add_rm_cmd(s):
    p = s.add_parser(
        'rm', help='删除容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    internal.add_arg_force(p)
    p.set_defaults(func=rm_cmd)


def rm_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'rm -f'
    if p.container:
        if not p.force and not internal.user_confirm('确认删除 ', p.container, '？'):
            raise er.UserCancel
        b += ' ' + ' '.join(p.container)
    if not p.force and not internal.user_confirm('确认删除所有容器？'):
        raise er.UserCancel
    return internal.docker_compose_cmd(b, host)

def add_start_cmd(s):
    p = s.add_parser(
        'start', help='启动容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    p.set_defaults(func=start_cmd)


def start_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'start'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, host)

def add_stop_cmd(s):
    p = s.add_parser(
        'stop', help='停止容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    p.set_defaults(func=stop_cmd)


def stop_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'stop'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, host)

def add_sync_cmd(s):
    p = s.add_parser(
        'sync', help='同步当前项目到远程路径')
    internal.add_arg_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=sync_cmd)
    p.add_argument('obj', type=str, default='ops', choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'ops'], nargs='?',
        help='''同步的对象。docker: docker-compose，ops 是除 var 和 volumes 的所有。默认：ops。
var, volumes 建议只用来同步初始数据。
同步 var, volumes 会检查远程目录是否为空文件夹，并做相应提示。''')


def sync_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    return internal.sync(host, p.force, p.obj)


def add_up_cmd(s):
    p = s.add_parser(
        'up', help='创建和启动容器。')
    internal.add_arg_host(p)
    internal.add_arg_container(p)
    p.set_defaults(func=up_cmd)


def up_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    b = 'up -d --remove-orphans'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, host)
