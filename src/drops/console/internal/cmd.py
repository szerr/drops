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
import time

import drops
from . import config
from . import internal
from . import er
from . import globa
from . import log

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
    internal.add_arg_force(p)
    p.set_defaults(func=backup_cmd)
    p.add_argument('obj', type=str, default='volumes', choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'ops', 'all'], nargs='?',
        help='''同步的文件夹。docker: docker-compose，ops 是除 var 和 volumes 的所有。''')
    p.add_argument('-t', '--target',
                   help="目标路径", default='backup')
    p.add_argument('-d', '--time-format', default='%Y-%m-%d_%H:%M:%S',
                   help='目标路径下创建文件夹名的时间模板，与 python time.strftime format 参数相同。如 %%Y-%%m-%%d_%%H:%%M:%%S')
    p.add_argument('-l', '--link-dest',
                   help='未更改时链接到指定文件夹。默认是备份路径中符合 format 排序后最大的文件夹。')
    p.add_argument('-k', '--keep',
                   type=int, help="保留的备份个数，只有 format 开启时启用。本次备份也算一个。-1 保留所有。", default='-1')
    p.add_argument("-c", '--cod',
                   help="在目标路径创建项目名命名的文件夹", default=False, action='store_true')


def backup_cmd(p):
    internal.check_env_arg()
    env = internal.config.Conf().gen_env_by_arg()
    if not os.path.isdir(p.target):
        os.mkdir(p.target)
    return internal.backup(env,  p.obj, p.target, p.time_format, p.link_dest, p.keep, p.cod, p.force)

def add_deploy_https_cert_cmd(s):
    p = s.add_parser(
        'deploy-https-cert', help='申请并部署 https 证书，基于 acme.sh。')
    p.add_argument("-f", '--force',
                   help="重新申请证书。", default=False, action='store_true')
    p.set_defaults(func=deploy_https_cert_cmd)


def deploy_https_cert_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'exec -T acme.sh redeploy-ssl'
    if p.force:
        b += ' --force'
    # redeploy-ssl 是作为文件映射进去的，需要重启才会更新。
    internal.docker_compose_cmd('restart acme.sh', env)
    print("开始申请证书，如果出现文件复制失败，请确认 nginx 容器是否正常运行。")
    print("如果域名没有变动，acme.sh 不会重新申请证书。--force 强制重新申请证书。")
    return internal.docker_compose_cmd(b, env)

def add_deploy_cmd(s):
    p = s.add_parser(
        'deploy', help='部署并启动服务。')
    internal.add_arg_force(p)
    p.set_defaults(func=deploy_cmd)


def deploy_cmd(p):
    internal.check_env_arg()
    env = internal.config.Conf().gen_env_by_arg()
    s = internal.sync(env, p.force)
    if s:
        return s
    return internal.docker_compose_cmd("up -d", env)

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
    p.add_argument('cmds',
                   help="要执行的命令。", type=str, nargs='+')
    p.set_defaults(func=exec_cmd)


def exec_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    internal.exec(internal.docker_cmd_template(
        "exec -T "+p.container + ' ' + ' '.join(p.cmds)), env)

def add_env_cmd(s):
    p = s.add_parser(
        'env', help='管理 drops 部署的环境连接配置。因为密码是明文存储的，建议用 key 做验证。')
    p.add_argument('cmd', type=str, choices=[
                   'ls', 'add', 'remove', 'change'], nargs='?', help="default ls")
    p.set_defaults(func=env_cmd)

def env_cmd(a):
    c = config.Conf().open()
    if a.cmd == 'add' or a.cmd == 'change':
        internal.check_env_arg()
        if a.cmd == 'add':
            if not globa.args.host:
                raise er.ArgsError("The -H(--host) argument is required.")
        env = config.gen_environment_by_arg(globa.args)
        c.set_env(globa.args.env, env).save()
    elif a.cmd == 'remove':
        internal.check_env_arg()
        c.remove_env(globa.args.env).save()
    elif a.cmd == 'ls':
        config.Conf().ls()
    else:
        config.Conf().ls()


def add_init_env_debian_cmd(s):
    p = s.add_parser(
        'init-debian-env', help='初始化 debian 系远程环境。')
    p.set_defaults(func=init_env_debian_cmd)


def init_env_debian_cmd(p):
    internal.check_env_arg()
    env = internal.config.Conf().gen_env_by_arg()
    bin = 'apt-get update && apt-get install -y rsync docker-compose'
    internal.exec(bin, env)

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

    config.Conf().new(pwd, p.projectName)

def add_new_cmd(s):
    p = s.add_parser(
        'new', help='Create a drops project.')
    p.add_argument("projectName",  type=str,
                   help="项目名。", default='', nargs='?')
    p.set_defaults(func=new_cmd)


def new_cmd(arg):
    from . import config
    from . import internal

    if arg.projectName in os.listdir(os.getcwd()):
        internal.Fatal("File exists: ", os.path.join(os.getcwd(), arg.projectName))
        return
    objPath = drops.__path__[0]
    shutil.copytree(os.path.join(objPath, 'docker_ops'),
                    os.path.join(os.getcwd(), arg.projectName))
    os.chdir(arg.projectName)
    config.Conf().new('drops.yaml', arg.projectName)

def add_kill_cmd(s):
    p = s.add_parser(
        'kill', help='杀掉容器。')
    internal.add_arg_container(p)
    p.set_defaults(func=kill_cmd)


def kill_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'kill'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, env)

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
    env = internal.config.Conf().gen_env_by_arg()
    b = 'logs '
    if p.follow:
        b += '-f '
    if p.loop:
        while True:
            internal.docker_compose_cmd(b+p.container, env)
            time.sleep(1)
    return internal.docker_compose_cmd(b+p.container, env)


def add_nginx_force_reload_cmd(s):
    p = s.add_parser(
        'nginx-force-reload', help="重载 nginx 配置，会重载证书。")
    p.set_defaults(func=nginx_force_reload_cmd)


def nginx_force_reload_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    internal.exec(internal.docker_cmd_template(
        "exec -T nginx nginx -g 'daemon on; master_process on;' -s reload"), env)

def add_nginx_reload_cmd(s):
    p = s.add_parser(
        'nginx-reload', help='重载 nginx 配置，不会重载证书。')
    p.set_defaults(func=nginx_reload_cmd)


def nginx_reload_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    return internal.docker_compose_cmd('exec -T nginx nginx -s reload', env)

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

def add_ps_cmd(s):
    p = s.add_parser(
        'ps', help='输出正在运行的容器。')
    p.set_defaults(func=ps_cmd)


def ps_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    return internal.docker_compose_cmd("ps", env)


def add_pull_cmd(s):
    p = s.add_parser(
        'pull', help='拉取容器。')
    internal.add_arg_container(p)
    p.set_defaults(func=pull_cmd)


def pull_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'pull'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, env)


def add_redeploy_cmd(s):
    p = s.add_parser(
        'redeploy', help='部署并启动服务，重新编译容器，移除不再用的容器。')
    internal.add_arg_force(p)
    p.set_defaults(func=redeploy_cmd)


def redeploy_cmd(p):
    internal.check_env_arg()
    env = internal.config.Conf().gen_env_by_arg()
    internal.sync(env, p.force)
    return internal.docker_compose_cmd("up -d --build --remove-orphans", env)

def add_restart_cmd(s):
    p = s.add_parser(
        'restart', help='重启容器。')
    internal.add_arg_container(p)
    p.set_defaults(func=restart_cmd)


def restart_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'restart'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, env)

def add_rm_cmd(s):
    p = s.add_parser(
        'rm', help='删除容器。')
    internal.add_arg_container(p)
    internal.add_arg_force(p)
    p.set_defaults(func=rm_cmd)


def rm_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'rm -f'
    if p.container:
        if not p.force and not internal.user_confirm('确认删除 ', ' '.join(p.container), '？'):
            raise er.UserCancel
        b += ' ' + ' '.join(p.container)
    elif not p.force and not internal.user_confirm('确认删除所有容器？'):
        raise er.UserCancel
    return internal.docker_compose_cmd(b, env)

def add_start_cmd(s):
    p = s.add_parser(
        'start', help='启动容器。')
    internal.add_arg_container(p)
    p.set_defaults(func=start_cmd)


def start_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'start'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, env)

def add_stop_cmd(s):
    p = s.add_parser(
        'stop', help='停止容器。')
    internal.add_arg_container(p)
    p.set_defaults(func=stop_cmd)


def stop_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'stop'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, env)

def add_sync_cmd(s):
    p = s.add_parser(
        'sync', help='同步当前项目到远程路径')
    internal.add_arg_force(p)
    p.set_defaults(func=sync_cmd)
    p.add_argument('obj', type=str, default='ops', choices=[
        'docker',  'release', 'image', 'var', 'volumes', 'ops'], nargs='?',
        help='''同步的对象。
ops 相当于 docker, release, image；
docker: docker-compose；
var, volumes 建议只用来同步初始数据。
同步 var, volumes 会检查远程目录是否为空文件夹，并做相应提示。''')


def sync_cmd(p):
    internal.check_env_arg()
    env = internal.config.Conf().gen_env_by_arg()
    return internal.sync(env, p.force, p.obj)


def add_up_cmd(s):
    p = s.add_parser(
        'up', help='创建和启动容器。')
    internal.add_arg_container(p)
    p.set_defaults(func=up_cmd)


def up_cmd(p):
    env = internal.config.Conf().gen_env_by_arg()
    b = 'up -d --remove-orphans'
    if p.container:
        b += ' ' + ' '.join(p.container)
    return internal.docker_compose_cmd(b, env)

def add_monitor_path_cmd(s):
    p = s.add_parser(
        'monitor-path', help='监视指定路径，接受文件变动后返回，或者执行命令。')
    p.add_argument("-p", '--path',  type=str,
                   help="指定监视的路径，默认 ./src", default='./src', nargs='?')
    p.add_argument('bin',  type=str,
                   help="要执行的命令。", default=[], nargs='*')
    internal.add_arg_container(p)
    p.set_defaults(func=monitor_path_cmd)

def monitor_path_cmd(p):
    # 监视文件夹，接受文件变动后返回0，或者执行命令。
    return internal.monitor_path(p.path, p.bin)

def add_build_cmd(s):
    p = s.add_parser(
        'build', help='执行所有项目的 script/build 脚本，优先级：py > sh > bat')
    p.add_argument("-p", '--project',
        help="指定一个或多个项目.", default=[], nargs='*', type=str)
    p.add_argument("-o", '--output',
        help="输出路径，每个项目创建一个文件夹。作为 -o 参数传给脚本。默认 ./release/[project]。", default='../../../release', nargs='?', type=str)
    p.add_argument("-c", '--clear',
        help="编译前清理目标文件夹。", default=False, action='store_true')
    internal.add_arg_container(p)
    p.set_defaults(func=build_cmd)

def build_cmd(p):
    pli = p.project
    if not pli:
        pli = os.listdir('src/')
    cwd = os.getcwd()
    for p_path in pli:
        print('--- build', p_path, '---')
        script_path = os.path.join('src', p_path, 'script')
        output_path = os.path.join(p.output, p_path)
        if not os.path.isdir(script_path):
            log.warning("There is no script for project", p_path)
            continue

        for b, e in (('python3', 'py'), ('python', 'py'), ('bash', 'sh'), ('sh', 'sh'), ('cmd.exe', 'bat')):
            f = 'build.'+e
            log.debug('test', b, f)
            if os.path.isfile(os.path.join(script_path, f)) and internal.command_exists(b):
                os.chdir(script_path)
                # 编译前是否清理目标目录
                if os.path.isdir(output_path):
                    if p.clear:
                        for i in os.listdir(output_path):
                            defpath = os.path.join(output_path,i)
                            if os.path.isdir(defpath):
                                shutil.rmtree(defpath)
                            if os.path.isfile(defpath):
                                os.remove(defpath)
                else:
                    os.makedirs(output_path)
                bin = b + ' ' + f + ' -o ' + output_path
                log.debug('run>', b + ' ' + f + ' -o ' + output_path)
                exit_code = internal.system(bin)
                if exit_code:
                    log.warning("build exit", exit_code)
                    return exit_code
                os.chdir(cwd)
                break
        else:
            log.warning("No supported build script found.")

# debug 模式下可用的命令：
def add_clean_up_cmd(s):
    p = s.add_parser(
        'clean', help='删除当前目录下 drops 所有相关文件。')
    internal.add_arg_force(p)
    p.set_defaults(func=new_clean_up)


def new_clean_up(p):
    if not p.force and not internal.user_confirm('是否清理掉当前目录的 drops 相关文件？'):
        raise er.UserCancel
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    pwd = os.getcwd()
    if not os.path.isfile(os.path.join(pwd, 'drops.yaml')):
        raise er.ThisIsNotDropsProject()
    for i in os.listdir(objPath):
        p = os.path.join(objPath, i)
        t = os.path.join(pwd, i)
        if os.path.isdir(p):
            shutil.rmtree(t)
        else:
            os.remove(t)

def add_undeploy_cmd(s):
    p = s.add_parser(
        'undeploy', help='清理掉服务器上的容器和项目')
    internal.add_arg_force(p)
    p.set_defaults(func=undeploy_cmd)


def undeploy_cmd(p):
    internal.check_env_arg()
    if not p.force and not internal.user_confirm('即将进行反部署，这会清理掉服务器上的容器及 '+internal.container_path()+' 目录，但不会完全删除映射文件。是否继续？'):
        raise er.UserCancel
    env = internal.config.Conf().gen_env_by_arg()
    print('---------- kill ----------')
    internal.docker_compose_cmd('kill', env)
    print('--------- rm -f ---------')
    internal.docker_compose_cmd('rm -f', env)
    print('-------- rm -rf %s --------' % internal.container_path())
    internal.exec('rm -rf %s' % internal.container_path(), env)
