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
import sys
import time
import shutil
import watchdog.events
import watchdog.observers
from fnmatch import fnmatch

import drops

from . import er, log
from . import system
from . import config
from . import globa
from . import helper


def new_project(path):
    name = os.path.split(path)[-1]
    os.mkdir(path)
    os.chdir(path)
    return init_project(name, path)


def init_project(name, path):
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    # 复制项目文件
    for i in os.listdir(objPath):
        s = os.path.join(objPath, i)
        t = os.path.join(path, i)
        if os.path.isdir(s):
            shutil.copytree(s, i)
        else:
            shutil.copyfile(s, i)
    # 初始化配置
    if globa.args.env:
        env = config.gen_env_by_args(name, globa.args)
        config.Conf().init_template(name).set_env(
            env).save(globa.args.config)
    else:
        config.Conf().init_template(name).save(globa.args.config)
    return 0


def rsync2remotely(env, src, target, exclude=[]):
    # rsync 本地同步到远程路径
    exclude = ' --exclude '.join(['', './.gitignore',
                                 './.git', './'+globa.args.config, './src', './secret'] + exclude)
    if env.identity_file:
        b = 'rsync -avzP --del -e "ssh -p {port} -i {key_path}" {exclude} {src} {username}@{host}:{target}'
        echo_b = b.format(
            src=src, target=target, key_path='<key_path>', port=env.port, username=env.username, host=env.host,
            exclude=exclude)
        b = b.format(
            src=src, target=target, key_path=env.identity_file, port=env.port, username=env.username, host=env.host,
            exclude=exclude)
    else:
        detection_cmd('sshpass')
        b = 'sshpass -p {password} rsync -avzP --del -e "ssh -p {port}" {exclude} {src} {username}@{host}:{target}'
        echo_b = b.format(
            src=src, target=target, password='<password>', port=env.port, username=env.username, host=env.host,
            exclude=exclude)
        b = b.format(
            src=src, target=target, password=env.password, port=env.port, username=env.username, host=env.host,
            exclude=exclude)
    log.run(echo_b)
    return system.system(b)

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
    # 本地命令是否存在
    for b in bl:
        for p in os.environ['PATH'].split(':'):
            if os.path.isdir(p) and b in os.listdir(p):
                break
        else:
            raise er.CmdNotExist(b)
    return True


def ssh_shell(env, b):
    detection_cmd('ssh')
    if env.identity_file:
        return system.system(helper.ssh_template_key(
            env.identity_file, env.port, env.username, env.host, b))
    else:
        detection_cmd('sshpass')
        return system.system(helper.ssh_template_pwd(
            env.password, env.port, env.username, env.host, b))


def rsync_release(env, force=False):
    print('------- sync release -------')
    detection_cmd('rsync')
    return rsync2remotely(env, 'release', env.deploy_path)


def rsync_docker(env, force=False):
    # 同步项目到远程目录
    print('------- sync docker-compose.yaml -------')
    detection_cmd('rsync')
    if 'docker-compose.yml' in os.listdir('.'):
        return rsync2remotely(env, 'docker-compose.yml', env.docker_compose_path())
    else:
        return rsync2remotely(env, 'docker-compose.yaml', env.docker_compose_path())


def rsync_servers(env, force=False):
    print('------- sync servers -------')
    detection_cmd('rsync')
    return rsync2remotely(env, 'servers', env.deploy_path)


def rsync_ops(env, force=False):
    # 同步 docker-compose.yaml release/ servers/
    print('------- sync ops -------')
    detection_cmd('rsync')
    s = 0
    if 'docker-compose.yml' in os.listdir('.'):
        s = rsync2remotely(env, 'docker-compose.yml',
                           env.docker_compose_path())
    else:
        s = rsync2remotely(env, 'docker-compose.yaml',
                           env.docker_compose_path())
    if s:
        return s

    s = rsync2remotely(env, 'release', env.get_deploy_path())
    if s:
        return s
    return rsync2remotely(env, 'servers', env.get_deploy_path())


def rsync_var(env, force):
    return rsync2remotely(env, 'var', env.get_deploy_path())


def rsync_volumes(env, force):
    # if not determine_drops_folder(env, env.volumes_path()):
    #     if not force and not user_confirm("主机 %s 远程目录 %s 不是空目录，是否继续同步？" % (env.host, env.volumes_path())):
    #         raise er.UserCancel
    return rsync2remotely(env, 'volumes', env.get_deploy_path())


def mkdir_deploy_path(env):
    # 创建远程文件夹
    c = system.SSH(env)
    _, status = c.exec(' mkdir -p ' + env.get_deploy_path())
    if status != 0:
        raise er.CmdExecutionError(
            'mkdir -p ' + env.get_deploy_path() + ', code=' + str(status))


def rsync_backup(env, src, target, link_desc=''):
    # rsync 备份
    # 设置 link_desc
    link = ''
    if link_desc:
        link = '--link-dest='+link_desc

    # 拼接命令
    if env.type == config.ENV_TYPE_REMOVE:
        if env.identity_file:
            temp = 'rsync -avzP --del -e "ssh -p {port} -i {identity_file}" {link_desc} {username}@{host}:{src} {target}'
        else:
            detection_cmd('sshpass')
            temp = 'sshpass -p {password} rsync -avzP --del -e "ssh -p {port}" {link_desc} {username}@{host}:{src} {target}'
    else:
        temp = 'rsync -avP --del {link_desc} {src} {target}'

    log.run(temp.format(src=src, target=target, port=env.port, username=env.username,
                        host=env.host, identity_file='<identity_file>', password='<pwd>', link_desc=link))
    cmd = temp.format(
        src=src, target=target, port=env.port, username=env.username,
        host=env.host, identity_file=env.identity_file,
        password=env.password, link_desc=link)
    return system.system(cmd)


def backup(env, obj, target, time_format='%Y-%m-%d_%H:%M:%S', link_desc='', keep_backups=-1, cod=False, force=False):
    # 如果 time_format 为空，会导致备份路径到 target 目录，删掉已有的备份。
    if not time_format:
        raise er.ArgsError('time_format cannot be empty.')
    time_format_dir = time.strftime(time_format)
    if not os.path.isdir(target):
        os.mkdir(target)
    backup2dir = target
    if cod:  # 创建项目名的文件夹
        backup2dir = os.path.join(
            backup2dir, env.project_name)
    # 备份文件夹模板
    backup2dir = os.path.join(backup2dir, '{obj}')
    # 需要备份的目录列表，路径结尾加上 / 代表同步目录下的文件，rsync 不会再创建一层目录。
    back_li = []
    if obj == 'all':
        back_li = [
            [env.release_path_dir(), backup2dir.format(obj='release')],
            [env.servers_path_dir(), backup2dir.format(obj='servers')],
            [env.var_path_dir(), backup2dir.format(obj='var')],
            [env.volumes_path_dir(), backup2dir.format(obj='volumes')],
            [env.docker_compose_path(), backup2dir.format(
                obj='docker-compose.yaml')],
        ]
    elif obj == 'ops':
        back_li = [
            [env.release_path_dir(), backup2dir.format(obj='release')],
            [env.servers_path_dir(), backup2dir.format(obj='servers')],
            [env.docker_compose_path(), backup2dir.format(
                obj='docker-compose.yaml')],
        ]
    elif obj == 'docker':
        back_li = [
            [env.docker_compose_path(), backup2dir.format(
                obj='docker-compose.yaml')],
        ]
    elif obj == 'release':
        back_li = [
            [env.release_path_dir(), backup2dir.format(obj='release')],
        ]
    elif obj == 'servers':
        back_li = [
            [env.servers_path_dir(), backup2dir.format(obj='servers')],
        ]
    elif obj == 'var':
        back_li = [
            [env.var_path_dir(), backup2dir.format(obj='var')],
        ]
    elif obj == 'volumes':
        back_li = [
            [env.volumes_path_dir(), backup2dir.format(obj='volumes')],
        ]
    else:
        raise er.UnsupportedBackupObject(obj)
    for source_path, backup_path in back_li:
        target_path = os.path.join(backup_path, time_format_dir)
        if not os.path.isdir(backup_path):
            os.makedirs(backup_path)

        # 查询已有的备份，准备做 --link-dest
        exist_li = os.listdir(backup_path)
        if time_format_dir in exist_li:
            exist_li.remove(time_format_dir)  # 移除本次要备份的目录

        # 过滤出符合 time_format 的文件夹
        exist_time_format_li = []
        for i in exist_li:
            try:
                time.strptime(i, time_format)
                exist_time_format_li.append(i)
            except ValueError as e:
                pass
        exist_time_format_li.sort(reverse=True)
        # 删除不需要保留的备份
        if keep_backups > 0:
            for r in exist_time_format_li[keep_backups:]:
                rd = os.path.join(backup_path, r)
                print('delete backup:', rd)
                # docker-compose.yaml 是文件，其他是目录
                if os.path.isdir(rd):
                    shutil.rmtree(rd)
                else:
                    os.remove(rd)
            exist_time_format_li = exist_time_format_li[:keep_backups]

        # 处理 link_desc
        link = link_desc
        if link_desc:
            if not link_desc in exist_li:
                raise er.ArgsError(
                    'link_desc: %s does not exist in the %s directory' % (link_desc, backup_path))
        else:  # 没有设置的话自动查找最大的文件夹
            if exist_time_format_li:
                link = os.path.join(
                    config.get_conf().work_path, backup_path, exist_time_format_li[0])
            else:
                log.info("%s 路径下没有找到合适 link 的文件夹，--link-dest 功能关闭。" %
                         backup_path)

        if not force and os.path.isdir(target_path) and os.listdir(target_path):
            if not user_confirm("备份路径 %s 已存在且非空，继续同步可能会导致文件丢失，是否继续同步？" % target_path):
                raise er.UserCancel

        s = rsync_backup(env, source_path, target_path, link)
        if s:
            return s
    return 0


def docker_compose_cmd(cmd, env):
    # docker_compose_cmd 解析命令行参数，只需要 ssh 部分的参数。
    # 接收一个字符串模板，
    # 拼接进入工作目录的命令，传入 cmd 并返回。
    # 可以执行任意 docker-compose 命令。
    for i in ('&', '`', '"', "'", ';'):  # 防止执行其他什么东西
        if i in cmd:
            raise er.CmdCannotContain(i)
    return exec(env.docker_cmd_template(cmd), env)


def exec(cmd, env, restart=False):
    # 对 env 执行任意命令, 如果没有设置 env，在当前目录执行。
    status = 0
    stdout = ""
    if env.type == config.ENV_TYPE_LOCAL:
        print('run host > localhost')
        print('command >', cmd)
        status = system.system(cmd)
    else:
        print('run host >', env.name)
        print('command >"', cmd)
        c = system.SSH(env)
        # 在远程路径下执行，要 cd 到项目目录
        stdout, status = c.exec(cmd)
    return status


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


def determine_drops_folder(env, path):
    # 返回 path 是否是空目录
    c = system.SSH(env)
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


def command_exists(b) -> bool:
    for cmdpath in os.environ['PATH'].split(':'):
        if os.path.isdir(cmdpath) and b in os.listdir(cmdpath):
            return True
    return False


def clean_up():
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    if not os.path.isfile(os.path.join(config.get_conf().work_path, 'drops.yaml')):
        raise er.ThisIsNotDropsProject()
    for i in os.listdir(objPath):
        p = os.path.join(objPath, i)
        t = os.path.join(config.get_conf().work_path, i)
        if os.path.isdir(p):
            shutil.rmtree(t)
        else:
            os.remove(t)


def build_src(dest, clear, project_li=[]):
    if not project_li:
        project_li = os.listdir('src/')
    for p_name in project_li:
        log.info('--- build', p_name, '---')
        script_dir = os.path.join(
            config.get_conf().work_path, 'src', p_name, 'drops')
        output_dir = os.path.join(dest, p_name)
        if not os.path.isdir(script_dir):
            log.warn(er.NoDropsDirProject(p_name))
            continue

        # 支持的脚本类型和解释器，按优先级排列
        for b, e in (('python3', 'py'), ('python', 'py'), ('bash', 'sh'), ('sh', 'sh'), ('cmd.exe', 'bat')):
            f = 'build.'+e
            log.debug('test', b, f)
            # 检查文件和相应解释器是否存在
            if os.path.isfile(os.path.join(script_dir, f)) and command_exists(b):
                break
        else:
            raise er.NoSupportedScriptFound(p_name)

        # 到脚本所在目录执行
        os.chdir(script_dir)
        log.info('chdir:', script_dir)
        # 编译前是否清理目标目录
        if os.path.isdir(output_dir):
            if clear:
                shutil.rmtree(output_dir)
                os.makedirs(output_dir)
        else:
            os.makedirs(output_dir)

        # 传给脚本输出目录的绝对路径
        bin = b + ' ' + f + ' --dest ' + os.path.abspath(output_dir)
        log.debug('run>', bin)
        # 错误码透传
        exit_code = system.system(bin)
        if exit_code:
            return exit_code
        os.chdir(config.get_conf().work_path)

    return 0


class FileSystemEventHander(watchdog.events.FileSystemEventHandler):
    def __init__(self, fn):
        # 处理文件系统事件，对每个事件调用 fn
        super(FileSystemEventHander, self).__init__()
        self.fn = fn

    def on_any_event(self, event):
        if event.event_type == 'modified':
            self.fn(event)


def watch_path(path, command, intervals):
    # 监视文件或文件夹路径，循环执行命令或退出。
    if not os.path.isdir(path) and not os.path.isfile(path):
        raise er.FileOrFolderDoesNotExist(path)
    observer = watchdog.observers.Observer()
    if command:
        p = helper.process(command, intervals)
        p.start()
        observer.schedule(FileSystemEventHander(p.add_event),
                          path, recursive=True)
    else:
        # 如果没有命令参数，收到事件后退出。
        observer.schedule(FileSystemEventHander(
            lambda x: sys.exit(0)), path, recursive=True)
    observer.start()

    try:
        observer.join()
    except:
        print("exiting....")
        p.exit()
        sys.exit(1)
    return 0
