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

from . import config
from . import biz
from . import er
from . import globa


def add_new_cmd(s):
    p = s.add_parser(
        'new', help='Create a drops project.')
    p.add_argument("project_path",  type=str,
                   help="项目路径，使用最后一个文件夹作为项目名。")
    p.set_defaults(func=new_cmd)


def new_cmd(p):
    if os.path.isdir(p.project_path) or os.path.isfile(p.project_path):
        raise er.FileOrDirAlreadyExists(p.project_path)
    return biz.new_project(p.project_path)


def add_version_cmd(s):
    p = s.add_parser(
        'version', help='输出版本号。')
    p.set_defaults(func=version_cmd)


def version_cmd(p):
    from .version import __version__
    print(__version__)
    return 0


def add_init_cmd(s):
    p = s.add_parser(
        'init', help='在当前目录初始化项目。')
    p.set_defaults(func=init_cmd)
    p.add_argument("project_name", help="项目名。")


def init_cmd(p):
    return biz.init_project(p.project_name, '.')


def add_backup_cmd(s):
    p = s.add_parser(
        'backup', help='基于 rsync 的增量备份。')
    p.set_defaults(func=backup_cmd)
    p.add_argument('obj', type=str, default='volumes', choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'ops', 'all'], nargs='?',
        help='''备份项目。docker: docker-compose，ops 是除 var 和 volumes 的所有。默认 volumes''')
    p.add_argument('-t', '--target',
                   help="目标路径", default='backup')
    p.add_argument('-d', '--time-format', default='%Y-%m-%d_%H:%M:%S',
                   help='目标路径下创建文件夹名的时间模板，与 python time.strftime format 参数相同。如 %%Y-%%m-%%d_%%H:%%M:%%S。也可以写字符串当 tag 用。')
    p.add_argument('-l', '--link-dest',
                   help='未更改时链接到指定文件夹。默认是备份路径中符合 format 排序后最大的文件夹。')
    p.add_argument('-k', '--keep-backups',
                   type=int, help="保留的备份个数，只管理符合 time-format 的文件夹。-1 保留所有。", default='-1')
    p.add_argument("-c", '--cod',
                   help="在目标路径创建项目名命名的文件夹", default=False, action='store_true')
    p.add_argument("-f", '--force',
                   help="不提示已存在的备份，不同步的文件会被覆盖或删除。", default=False, action='store_true')


def backup_cmd(p):
    env = config.get_env()
    if not p.time_format:
        raise er.ArgsError('time_format cannot be empty.')
    return biz.backup(env,  p.obj, p.target, p.time_format, p.link_dest, p.keep_backups, p.cod, p.force)


def add_deploy_https_cert_cmd(s):
    p = s.add_parser(
        'deploy-https-cert', help='申请并部署 https 证书，基于 acme.sh。')
    p.add_argument("-f", '--force',
                   help="重新申请证书。", default=False, action='store_true')
    p.set_defaults(func=deploy_https_cert_cmd)


def deploy_https_cert_cmd(p):
    env = config.get_env()
    b = 'exec -T acme.sh redeploy-ssl'
    if p.force:
        b += ' --force'
    # redeploy-ssl 是作为文件映射进去的，需要重启才会更新。
    biz.docker_compose_cmd('restart acme.sh', env)
    print("开始申请证书，如果出现文件复制失败，请确认 nginx 容器是否正常运行。")
    print("如果域名没有变动，acme.sh 不会重新申请证书。--force 强制重新申请证书。")
    return biz.docker_compose_cmd(b, env)


def add_deploy_cmd(s):
    p = s.add_parser(
        'deploy', help='部署并启动服务。')
    biz.add_arg_force(p)
    p.set_defaults(func=deploy_cmd)


def deploy_cmd(p):
    env = config.get_env()
    biz.mkdir_deploy_path(env)
    s = biz.rsync_ops(env, p.force)
    if s:
        return s
    return biz.docker_compose_cmd("up -d", env)


def add_echo_paths_cmd(s):
    p = s.add_parser(
        'echo-paths', help='显示 drops 用到的各部署路径')
    p.set_defaults(func=deploy_echo_paths_cmd)


def deploy_echo_paths_cmd(p):
    env = config.get_env()
    print('容器路径，docker-compose.yaml 所在文件夹:', env.container_path())
    print('发布路径，应用程序文件夹:', env.release_path())
    print('volumes 路径，应用程序数据文件夹:', env.volumes_path())
    return 0


def add_exec_cmd(s):
    p = s.add_parser(
        'exec', help='在任意容器中执行命令。')
    p.add_argument("container", metavar="container",
                   type=str, help="容器名")
    p.add_argument('cmds',
                   help="要执行的命令。", type=str, nargs='+')
    p.add_argument('-r', '--restart', default=False, action='store_true',
                   help="restart on failure. interval 3 seconds.")
    p.set_defaults(func=exec_cmd)


def exec_cmd(p):
    failed_times = 0
    env = config.get_env()
    while True:
        status = biz.exec(env.docker_cmd_template(
            "exec -T "+p.container + ' ' + ' '.join(p.cmds)), env, p.restart)
        if p.restart:
            if status:
                failed_times += 1
                sleep = failed_times % 60
                print('exit status: %d, sleep: %ds....' % (status, sleep))
                time.sleep(sleep)
            else:
                failed_times = 0
        else:
            break


def add_env_cmd(s):
    p = s.add_parser(
        'env', help='管理 drops 部署的环境连接配置。因为密码是明文存储的，建议用 key 做验证。')
    p.add_argument('cmd', type=str, choices=[
                   'ls', 'add', 'remove', 'change'], nargs='?', help="default ls")
    p.set_defaults(func=env_cmd)


def env_cmd(a):
    c = config.Conf().open()
    if a.cmd == 'add' or a.cmd == 'change':
        env = config.get_env()
        if a.cmd == 'add':
            if not globa.args.host:
                raise er.ArgsError("The -H(--host) argument is required.")
        c.set_env(env).save()
    elif a.cmd == 'remove':
        env = config.get_env()
        c.remove_env(globa.args.env).save()
    elif a.cmd == 'ls':
        config.Conf().ls()
    else:
        config.Conf().ls()
    return 0


def add_init_env_debian_cmd(s):
    p = s.add_parser(
        'init-debian-env', help='初始化 debian 系远程环境。')
    p.set_defaults(func=init_env_debian_cmd)


def init_env_debian_cmd(p):
    env = config.get_env()

    bin = 'apt-get update && apt-get install -y rsync docker-compose'
    return biz.exec(bin, env)


def add_kill_cmd(s):
    p = s.add_parser(
        'kill', help='杀掉容器。')
    biz.add_arg_container(p)
    p.set_defaults(func=kill_cmd)


def kill_cmd(p):
    b = 'kill'
    if p.container:
        b += ' ' + ' '.join(p.container)
    env = config.get_env()
    return biz.docker_compose_cmd(b, env)


def add_logs_cmd(s):
    p = s.add_parser(
        'logs', help='输出容器日志。')
    p.add_argument("container", metavar="container",
                   type=str, help="容器名")
    p.add_argument("-f", '--follow',
                   help="持续日志输出。", default=False, action='store_true')
    p.add_argument("-l", '--loop',
                   help="循坏输出，容器重启后重新运行。", default=False, action='store_true')
    p.set_defaults(func=logs_cmd)


def logs_cmd(p):
    b = 'logs '
    if p.follow:
        b += '-f '
    env = config.get_env()
    if p.loop:
        while True:
            biz.docker_compose_cmd(b+p.container, env)
            time.sleep(1)
    return biz.docker_compose_cmd(b+p.container, env)


def add_nginx_force_reload_cmd(s):
    p = s.add_parser(
        'nginx-force-reload', help="重载 nginx 配置，会重载证书。")
    p.set_defaults(func=nginx_force_reload_cmd)


def nginx_force_reload_cmd(p):
    env = config.get_env()
    return biz.exec(env.docker_cmd_template("exec -T nginx nginx -g 'daemon on; master_process on;' -s reload"), env)


def add_nginx_reload_cmd(s):
    p = s.add_parser(
        'nginx-reload', help='重载 nginx 配置，不会重载证书。')
    p.set_defaults(func=nginx_reload_cmd)


def nginx_reload_cmd(p):
    env = config.get_env()
    return biz.docker_compose_cmd('exec -T nginx nginx -s reload', env)


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
            print(c.project_name())
        else:
            c.set_project_name(p.name)
    else:
        for k, i in c._data['project'].items():
            print(k, ': ', i, sep='')
    return 0


def add_ps_cmd(s):
    p = s.add_parser(
        'ps', help='输出正在运行的容器。')
    p.set_defaults(func=ps_cmd)


def ps_cmd(p):
    env = config.get_env()
    return biz.docker_compose_cmd("ps", env)


def add_pull_cmd(s):
    p = s.add_parser(
        'pull', help='拉取容器。')
    biz.add_arg_container(p)
    p.set_defaults(func=pull_cmd)


def pull_cmd(p):
    b = 'pull'
    if p.container:
        b += ' ' + ' '.join(p.container)
    env = config.get_env()
    return biz.docker_compose_cmd(b, env)


def add_redeploy_cmd(s):
    p = s.add_parser(
        'redeploy', help='部署并启动服务，重新编译容器，移除不再用的容器。')
    biz.add_arg_force(p)
    p.set_defaults(func=redeploy_cmd)


def redeploy_cmd(p):
    env = config.get_env()

    biz.rsync_ops(env, p.force)
    return biz.docker_compose_cmd("up -d --build --remove-orphans", env)


def add_restart_cmd(s):
    p = s.add_parser(
        'restart', help='重启容器。')
    biz.add_arg_container(p)
    p.set_defaults(func=restart_cmd)


def restart_cmd(p):
    b = 'restart'
    if p.container:
        b += ' ' + ' '.join(p.container)
    env = config.get_env()
    return biz.docker_compose_cmd(b, env)


def add_rm_cmd(s):
    p = s.add_parser(
        'rm', help='删除容器。')
    biz.add_arg_container(p)
    biz.add_arg_force(p)
    p.set_defaults(func=rm_cmd)


def rm_cmd(p):
    b = 'rm -f'
    if p.container:
        if not p.force and not biz.user_confirm('确认删除 ', ' '.join(p.container), '？'):
            raise er.UserCancel
        b += ' ' + ' '.join(p.container)
    elif not p.force and not biz.user_confirm('确认删除所有容器？'):
        raise er.UserCancel
    env = config.get_env()
    return biz.docker_compose_cmd(b, env)


def add_start_cmd(s):
    p = s.add_parser(
        'start', help='启动容器。')
    biz.add_arg_container(p)
    p.set_defaults(func=start_cmd)


def start_cmd(p):
    b = 'start'
    if p.container:
        b += ' ' + ' '.join(p.container)
    env = config.get_env()
    return biz.docker_compose_cmd(b, env)


def add_stop_cmd(s):
    p = s.add_parser(
        'stop', help='停止容器。')
    biz.add_arg_container(p)
    p.set_defaults(func=stop_cmd)


def stop_cmd(p):
    b = 'stop'
    if p.container:
        b += ' ' + ' '.join(p.container)
    env = config.get_env()
    return biz.docker_compose_cmd(b, env)


def add_sync_cmd(s):
    p = s.add_parser(
        'sync', help='同步当前项目到远程路径')
    biz.add_arg_force(p)
    p.set_defaults(func=sync_cmd)
    p.add_argument('obj', type=str, default='ops', choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'ops'], nargs='?',
        help='''同步的对象。
ops 相当于 docker, release, servers；
docker: docker-compose；
var, volumes 建议只用来同步初始数据。
同步 var, volumes 会检查远程目录是否为空文件夹，并做相应提示。''')


def sync_cmd(p):
    env = config.get_env()
    biz.mkdir_deploy_path(env)
    if p.obj == 'ops':
        return biz.rsync_ops(env, p.force)
    elif p.obj == 'docker':
        return biz.rsync_docker(env, p.force)
    elif p.obj == 'release':
        return biz.rsync_release(env, p.force)
    elif p.obj == 'servers':
        return biz.rsync_servers(env, p.force)
    elif p.obj == 'var':
        return biz.rsync_var(env, p.force)
    elif p.obj == 'volumes':
        return biz.rsync_volumes(env, p.force)
    else:
        raise er.UnsupportedSyncObject(p.obj)


def add_up_cmd(s):
    p = s.add_parser(
        'up', help='创建和启动容器。')
    biz.add_arg_container(p)
    p.set_defaults(func=up_cmd)


def up_cmd(p):
    b = 'up -d --remove-orphans'
    env = config.get_env()
    if p.container:
        b += ' ' + ' '.join(p.container)
    return biz.docker_compose_cmd(b, env)


def add_watch_cmd(s):
    p = s.add_parser(
        'watch', help='监视文件系统事件，执行传入的 command。触发事件后 SIGKILL command 进程并重启。没有 command 则阻塞直到有事件后返回。（测试功能）')
    p.add_argument("-p", '--path',  type=str,
                   help="指定监视的路径，默认 ./src", default='./src', nargs='?')
    p.add_argument("-n", '--intervals',  type=int,
                   help="重启之间等待的秒数。默认3s。", default=3, nargs='?')
    p.add_argument('command',  type=str,
                   help="要执行的命令，触发事件后杀掉并重启。", default=[], nargs='*')
    biz.add_arg_container(p)
    p.set_defaults(func=watch_cmd)


def watch_cmd(p):
    # 监视文件夹，接受文件变动后返回0，或者执行命令。
    return biz.watch_path(p.path, p.command, p.intervals)


def add_build_cmd(s):
    p = s.add_parser(
        'build', help='执行所有项目的 drops/build 脚本，优先级：py > sh > bat')
    p.add_argument('project',
                   help="指定一个或多个项目.", default=[], nargs='*', type=str)
    # 因为 bash
    p.add_argument("-d", '--dest',
                   help="输出目录的绝对路径，drops 会给每个项目创建一个目录，作为 --dest 参数传给脚本。默认 ./release/[project]。", default='../../../release', nargs='?', type=str)
    p.add_argument("-c", '--clear',
                   help="编译前清理目标文件夹。", default=False, action='store_true')
    biz.add_arg_container(p)
    p.set_defaults(func=build_cmd)


def build_cmd(arg):
    pli = arg.project
    return biz.build_src(arg.dest, arg.clear, arg.project)

# debug 模式下可用的命令：


def add_clean_up_cmd(s):
    p = s.add_parser(
        'clean', help='删除当前目录下 drops 所有相关文件。')
    biz.add_arg_force(p)
    p.set_defaults(func=new_clean_up_cmd)


def new_clean_up_cmd(p):
    if not p.force and not biz.user_confirm('是否清理掉当前目录的 drops 相关文件？'):
        raise er.UserCancel
    return biz.clean_up()


def add_undeploy_cmd(s):
    p = s.add_parser(
        'undeploy', help='清理掉服务器上的容器和项目')
    biz.add_arg_force(p)
    p.set_defaults(func=undeploy_cmd)


def undeploy_cmd(p):
    env = config.get_env()
    if not p.force and not biz.user_confirm('即将进行反部署，这会清理掉服务器上的容器及 '+env.container_path()+' 目录，但不会完全删除映射文件。是否继续？'):
        raise er.UserCancel

    status = 0
    print('---------- kill ----------')
    status = biz.docker_compose_cmd('kill', env)
    if status:
        return status
    print('--------- rm -f ---------')
    status = biz.docker_compose_cmd('rm -f', env)
    if status:
        return
    print('-------- rm -rf %s --------' % env.container_path())
    return biz.exec('rm -rf %s' % env.container_path(), env)
