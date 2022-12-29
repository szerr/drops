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

from . import er
from . import globals
from . import ssh
from . import config

port = 22  # 默认端口
deploy_path = "/usr/local/drops/"  # 部署到服务器的路径
# 进入工作目录，默认是项目所在目录的目录名，部署时会同步文件到这个路径。


def work_dir():
    c = config.Conf()
    return deploy_path + c.getProjectName()


def docker_cmd_template(cmd):
    # 执行 docker-compose 命令的模板，看起来像是这样：
    #  cd <work_dir> && docker-compose %s"
    return 'cd ' + work_dir() + ' && docker-compose %s' % cmd


# rsync 同步文件的命令模板
def rsync_cmd_template_key(password, port, username, host):
    # key 登录
    return ('rsync -avzP --del -e "ssh -p %d -i %s" --exclude "drops.yaml" --exclude ".git" --exclude ".gitignore" . %s@%s:'+work_dir()) % (password, port, username, host)


def rsync_cmd_template_pwd(password, port, username, host):
    # 密码登录
    return ('sshpass -p %s rsync -avzP --del -e "ssh -p %d" --exclude "drops.yaml" --exclude ".git" --exclude ".gitignore" . %s@%s:'+work_dir()) % (password, port, username, host)


def Fatal(*e):
    print("Fatal!", *e)


def add_ssh_arg(p):
    p.add_argument('-h', type=str, help='host', required=False)
    p.add_argument('-p', '--port', dest='port', type=int,
                   help="ssh port", default=0)


def add_container_arg(p):
    p.add_argument('container', type=str,
                   help="docker container name", nargs=1)


def add_cmd_arg(p):
    p.add_argument('cmd', type=str,
                   help="docker-compose <cmd>", nargs='+', default='')


def add_arg_service(p):
    p.add_argument("-s", "--service",
                   help="docker service name.", type=str, default=None)


def add_arg_force(p):
    p.add_argument("-f", '--force',
                   help="强制执行，不再提示确认。", default=False, action='store_true')


def add_arg_group(p):
    p.add_argument("group",
                   help="host group.", type=str, default='test', nargs='?')


def get_arg_group_from_conf(p):
    return config.Conf().get_group(p.group)


def add_arg_group_host(p):
    add_arg_group(p)
    p.add_argument('hosts',
                   help="hosts.", type=int, nargs='*')


def get_arg_group_host_from_conf(p):
    return config.Conf().get_hosts(p.group, p.hosts)


def parse_args(p):
    return p.parse_args()


def gen_ssh_cmd():
    per = parse_args()
    if per.port:
        port = "-p %d" % per.port
    else:
        port = ""
    return ssh_cmd_template % (per.destination[0], port)


def detection_cmd(b):
    # 确认命令是否存在
    for p in os.environ['PATH'].split(':'):
        if os.path.isdir(p) and b in os.listdir(p):
            return True
    else:
        return False


def rsync_cmd(hosts, force=False):
    # 同步项目到远程目录
    if not detection_cmd('rsync'):
        raise er.RsyncNotExist
    for host in hosts.values():
        # if not confirmDropsProject(i):
        #     return
        if not force and not confirm_drops_project(host):
            if not user_confirm("主机 %s 远程目录可能不是 drops 项目，是否继续同步？" % host.host):
                raise er.UserCancel
        c = ssh.Client(**host.to_conf())
        _, status = c.exec(' mkdir -p ' + deploy_path)
        if status != 0:
            raise er.CmdExecutionError('mkdir -p ' + deploy_path)
        if host.key:
            os.system(rsync_cmd_template_key(
                host.port, host.key, host.username, host.host))
        else:
            os.system(rsync_cmd_template_pwd(
                host.password, host.port, host.username, host.host))


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
            a = input(s + '[Y/n]')
        except KeyboardInterrupt:
            return False
        if a == 'Y':
            return True
        elif a == 'n':
            return False
    return False


def confirm_drops_project(host):
    # 防止出现同步时误删除，同步前检查目录。
    c = ssh.Client(**host.to_conf())

    # 目录存在返回0，否则返回1
    while True:
        _, s = c.exec(
            '''if [ -d %s ]; then exit 0; else exit 1; fi''' % work_dir(), False)
        if s != -1:
            break
    # 目录不存在时可以安全同步
    if s == 1:
        return True
    b = '''if [ -f %s ] && [ -d %s ]; then exit 0; else exit 1; fi''' % (
        work_dir()+'/docker-compose.yaml', work_dir()+'/servers')

    while True:
        _, s = c.exec(b, False)
        # 这条命令很容易返回 -1，貌似是 paramiko 的锅。重试。
        if s != -1:
            break
    # 目录存在，却没有 docker-compose 或 servers，可能不是 drops 项目
    if s == 0:
        return True
    return False
