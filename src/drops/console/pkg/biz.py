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
import subprocess
import threading
from fnmatch import fnmatch

import drops

from . import er, log
from . import system
from . import config
from . import globa
from . import helper


def get_work_path():
    # 当前 drops 项目绝对路径，drops.yaml 所在目录
    return os.getcwd()


def new_project(name, path):
    os.chdir(path)
    os.mkdir(name)
    return init_project(name, os.path.join(path, name))


def init_project(name, path):
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    # 复制项目文件
    for i in os.listdir(objPath):
        s = os.path.join(objPath, i)
        t = os.path.join(path, i)
        if os.path.isdir(s):
            shutil.copytree(s, t)
        else:
            shutil.copyfile(s, t)

    # 初始化配置
    if globa.args.env:
        env = config.gen_env_by_args(globa.args)
        config.Conf().init_template(name).set_env(
            env).save(os.path.join(path, globa.args.config))
    else:
        config.Conf().init_template(name).save(os.path.join(path, globa.args.config))
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


def rsync2local(env, src, target):
    # rsync 远程同步到本地
    if env.identity_file:
        b = 'rsync -avzP --del -e "ssh -p {port} -i %s" {username}@{host}:{src} {target}'.format(
            src=src, target=target, port=env.port, username=env.username, host=env.host)
        print(b % ('<key_path>'))
        b = b % env.identity_file
    else:
        detection_cmd('sshpass')
        b = 'sshpass -p %s rsync -avzP --del -e "ssh -p {port}" {username}@{host}:{src} {target}'.format(
            src=src, target=target, port=env.port, username=env.username, host=env.host)
        print(b % ('<password>'))
        b = b % env.password
    return system.system(b)


def rsync2local_link_dest(env, src, target, link_dest):
    # rsync 远程同步到本地，设置链接
    if env.identity_file:
        b = 'rsync -avzP --del -e "ssh -p {port} -i %s" --link-dest={link_dest} {username}@{host}:{src} {target}'.format(
            src=src, target=target, port=env.port, username=env.username, host=env.host, link_dest=link_dest)
        print(b)
        b = b % env.identity_file
    else:
        detection_cmd('sshpass')
        b = 'sshpass -p {%s} rsync -avzP --del -e "ssh -p {port}" --link-dest={link_dest} {username}@{host}:{src} {target}'.format(
            src=src, target=target, port=env.port, username=env.username, host=env.host, link_dest=link_dest)
        print(b)
        b = b % env.password
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
    return rsync2remotely(env, 'docker-compose.yaml', env.docker_compose_path())


def rsync_servers(env, force=False):
    print('------- sync servers -------')
    detection_cmd('rsync')
    return rsync2remotely(env, 'servers', env.deploy_path)


def rsync_ops(env, force=False):
    print('------- sync ops -------')
    detection_cmd('rsync')
    exclude = [i for i in os.listdir(get_work_path()) if
               not i in ['docker-compose.yaml', 'docker-compose.yml', 'release', 'servers']]
    return rsync2remotely(env, '.', env.deploy_path, exclude)


def rsync_var(env, force):
    return rsync2remotely(env, 'var', env.get_deploy_path())


def rsync_volumes(env, force):
    # if not determine_drops_folder(env, env.volumes_path()):
    #     if not force and not user_confirm("主机 %s 远程目录 %s 不是空目录，是否继续同步？" % (env.host, env.volumes_path())):
    #         raise er.UserCancel
    return rsync2remotely(env, 'volumes', env.get_deploy_path())


def mkdir_deploy(env):
    # 创建远程文件夹
    c = system.SSH(env)
    _, status = c.exec(' mkdir -p ' + env.get_deploy_path())
    if status != 0:
        raise er.CmdExecutionError(
            'mkdir -p ' + env.get_deploy_path() + ', code=' + str(status))


def rsync_backup(env, src, target, link_desc=''):
    detection_cmd('rsync')
    if link_desc:
        return rsync2local_link_dest(env, src, target, link_desc)
    return rsync2local(env, src, target)


def backup(env, obj, target, time_format='%Y-%m-%d_%H:%M:%S', link_desc='', keep_backups=-1, cod=False, force=False):
    backup2dir = target
    link_dir = link_desc
    if cod:  # 创建项目名的文件夹
        backup2dir = os.path.join(backup2dir, config.Conf().project_name())
    # 如果设定了时间格式
    if time_format:
        # 备份目录是备份对象下的时间目录
        backup2dir = os.path.join(backup2dir, '{obj}')
        # 如果设置了 link_desc
    # 需要备份的目录列表，路径结尾加上 / 代表同步目录下的文件，rsync 不会再创建一层目录。
    back_li = []
    if obj == 'all':
        back_li = [
            [env.release_path() + '/', backup2dir.format(obj='release')],
            [env.servers_path() + '/', backup2dir.format(obj='servers')],
            [env.var_path() + '/', backup2dir.format(obj='var')],
            [env.volumes_path() + '/', backup2dir.format(obj='volumes')],
            [env.docker_compose_path(), backup2dir.format(
                obj='docker-compose.yaml')],
        ]
    elif obj == 'ops':
        back_li = [
            [env.release_path() + '/', backup2dir.format(obj='release')],
            [env.servers_path() + '/', backup2dir.format(obj='servers')],
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
            [env.release_path() + '/', backup2dir.format(obj='release')],
        ]
    elif obj == 'servers':
        back_li = [
            [env.servers_path() + '/', backup2dir.format(obj='servers')],
        ]
    elif obj == 'var':
        back_li = [
            [env.var_path() + '/', backup2dir.format(obj='var')],
        ]
    elif obj == 'volumes':
        back_li = [
            [env.volumes_path() + '/', backup2dir.format(obj='volumes')],
        ]
    else:
        raise er.UnsupportedBackupObject(obj)
    for source_path, target_path in back_li:
        if not os.path.isdir(target_path):
            os.mkdir(target_path)
        # 生成带有时间的备份路径
        backup_time = time.strftime(time_format, time.localtime(time.time()))
        backup2path = os.path.join(target_path, backup_time)
        exist_li = os.listdir(target_path)
        exist_li.sort(reverse=True)

        if not force and os.path.isdir(backup2path) and os.listdir(backup2path):
            if not user_confirm("备份路径 %s 已存在且非空，继续同步可能会导致文件丢失，是否继续同步？" % backup2path):
                raise er.UserCancel

        # 如果本次要备份的路径已存在，移除掉，避免重复计算
        if backup_time in exist_li:
            exist_li.remove(backup_time)
        if keep_backups > 0:  # 删除不需要保留的备份
            for r in exist_li[keep_backups:]:
                rd = os.path.join(target_path, r)
                print('delete backup:', rd)
                # docker-compose.yaml 是文件，其他是目录
                if os.path.isdir(rd):
                    shutil.rmtree(rd)
                else:
                    os.remove(rd)
            exist_li = exist_li[keep_backups:]

        if not link_desc:  # 没有传入 link desc，自动寻找最新备份执行 link desc。
            if exist_li:
                # link 目录是排序后最大的目录
                link_dir = exist_li[0]
                link_desc = os.path.join(
                    get_work_path(), target_path, link_dir)
            else:
                print("%s 路径下没有找到合适的备份文件夹，--link-dest 功能关闭。" % target_path)
        s = rsync_backup(env, source_path, backup2path, link_desc)
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
        print('run host >', env.env)
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


class FileSystemEventHander(watchdog.events.FileSystemEventHandler):
    def __init__(self, fn):
        super(FileSystemEventHander, self).__init__()
        self.restart = fn

    def on_any_event(self, event):
        if event.event_type == 'modified':
            self.restart(event)


class process():
    def __init__(self, command, intervals):
        self._intervals = intervals  # 重启间隔时间
        self._command_str = ' '.join(command)
        self._command = [
            i for i in self._command_str.split(' ') if i]  # 形成参数数组
        self._process = None
        self._event_li = []
        self._run_status = True
        self._t = threading.Thread(target=self.periodicRestart)
        self._t.start()

    def exit(self):
        self._run_status = False
        self.stop()

    def start(self):
        print("run>", self._command_str)
        self._process = subprocess.Popen(
            self._command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    def stop(self):
        if self._process:
            print("kill>", self._command_str)
            self._process.kill()
            print("Wait for exit...")
            self._process.wait()

    def restart(self):
        self.stop()
        self.start()

    def add_event(self, e):
        self._event_li.append(e)

    def periodicRestart(self):
        # 每次保存可能会触发多个更改事件，增加计时器减少重启的次数。
        while self._run_status and not globa.thread_exit:
            time.sleep(self._intervals)
            if self._event_li:
                print("Number of file system.system events:", len(self._event_li))
                self._event_li = []
                self.restart()


def clean_up():
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    pwd = get_work_path()
    if not os.path.isfile(os.path.join(pwd, 'drops.yaml')):
        raise er.ThisIsNotDropsProject()
    for i in os.listdir(objPath):
        p = os.path.join(objPath, i)
        t = os.path.join(pwd, i)
        if os.path.isdir(p):
            shutil.rmtree(t)
        else:
            os.remove(t)


def build_src(dest, clear, project_li=[]):
    if not project_li:
        project_li = os.listdir('src/')
    work_path = get_work_path()
    for p_name in project_li:
        log.info('--- build', p_name, '---')
        script_dir = os.path.join(work_path, 'src', p_name, 'drops')
        output_dir = os.path.join(dest, p_name)
        if not os.path.isdir(script_dir):
            raise er.NoScriptForProject(p_name)

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
        os.chdir(work_path)

    return 0


def monitor_path(path, command, intervals):
    if not os.path.isdir(path) and not os.path.isfile(path):
        raise er.FileOrFolderDoesNotExist(path)
    observer = watchdog.observers.Observer()
    if command:
        p = process(command, intervals)
        p.start()
        observer.schedule(watchdog.events.Filesystem.systemEventHander(
            p.add_event), path, recursive=True)
    else:
        # 如果没有命令参数，收到事件后退出。
        observer.schedule(watchdog.events.Filesystem.systemEventHander(
            lambda: sys.exit(0)), path, recursive=True)
    observer.start()

    try:
        observer.join()
    except:
        print("exiting....")
        p.exit()
        sys.exit(1)
    return 0