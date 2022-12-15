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
deploy_path = "/usr/local/"  # 部署到服务器的路径
# 进入工作目录，默认是项目所在目录的目录名，部署时会同步文件到这个路径。
work_dir = deploy_path + os.path.split(os.getcwd())[-1]

# 切换到工作目录的命令
go_to_work_dir = 'cd ' + work_dir

# 结合 ssh，登录后切换到工作目录执行命令的模板，整体看起来像是这样：
#  "cd <work_dir> && %s"
go_to_work_dir_template = ' "cd ' + work_dir + ' && %s"'

# 执行 docker-compose 命令的模板，看起来像是这样：
#  cd <work_dir> && docker-compose %s"
docker_cmd_template = 'cd ' + \
    work_dir + ' && docker-compose %s'

# rsync 同步文件的命令模板
# key 登录
rsync_cmd_template_key = '''rsync -avzP --del -e "ssh -p %d -i %s" --exclude ".git" --exclude ".gitignore" . %s@%s:'''+work_dir
# 密码登录
rsync_cmd_template_pwd = '''sshpass -p %s rsync -avzP --del -e "ssh -p %d" --exclude ".git" --exclude ".gitignore" . %s@%s:'''+work_dir


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
    for p in os.environ['PATH'].split(':'):
        if os.path.isdir(p) and b in os.listdir(p):
            return True
    else:
        return False


def rsync_cmd(hosts):
    # 同步项目到远程目录
    if not detection_cmd('rsync'):
        raise er.RsyncNotExist
    for i in hosts.values():
        if i.key:
            os.system(rsync_cmd_template_key %
                      (i.port, i.key, i.username, i.host))
        else:
            os.system(rsync_cmd_template_pwd %
                      (i.password, i.port, i.username, i.host))


def docker_cmd(template):
    # docker_cmd 解析命令行参数，获取 <container> <cmd>
    # 接收一个字符串模板，内容是 docker-compose 后的部分
    # 拼接进入工作目录的命令，先后传入 (container, cmd) 并返回。
    # 对特定容器执行命令。

    add_container_arg()

    template = template % (p.container[0], '%s')
    template = template % (' '.join(p.cmd))
    if p.port:
        port = "-p %d" % p.port
    else:
        port = ""
    return go_to_work_dir_template % (p.destination[0], port, template)


def docker_container(template):
    # docker_container 解析命令行参数，获取 <container>
    # 接收一个字符串模板，内容是 docker-compose 后的部分
    # 拼接进入工作目录的命令，传入 container 并返回。
    # 对特定容器执行命令。

    add_container_arg()

    template = template % (p.container[0])
    if p.port:
        port = "-p %d" % p.port
    else:
        port = ""
    return go_to_work_dir_template % (p.destination[0], port, template)


def docker_container_cmd(p, desc):
    # docker_container_cmd 解析命令行参数，获取 <cmd>
    # 执行 docker-compose <cmd>

    if p.port:
        port = "-p %d" % p.port
    else:
        port = ""
    return docker_cmd_template % (p.destination[0], port, ' '.join(p.cmd))


def docker_compose_cmd(cmd, hosts):
    # docker_compose_cmd 解析命令行参数，只需要 ssh 部分的参数。
    # 接收一个字符串模板，
    # 拼接进入工作目录的命令，传入 cmd 并返回。
    # 可以执行任意 docker-compose 命令。
    for i in ('&', '`', '"', "'", ';'):  # 防止执行其他什么东西
        if i in cmd:
            raise er.CmdCannotContain(i)
    return exec(docker_cmd_template % cmd, hosts)


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


def exed(cmd, hosts):
    # 之前的命令执行方式，备份代码。
    # 对 host 执行任意远程命令
    result = {}
    for host in hosts.values():
        c = ssh.Client(**host.to_conf())
        result[host.host] = c.exed(cmd)

    success = {k: i for k, i in result.items() if i[2] == 0}
    fail = {k: i for k, i in result.items() if i[2] != 0}

    print('---------------- success ----------------')
    for k, i in success.items():
        print(k)
        print(i[0])
        if i[1]:
            print(i[1])

    if fail:
        print('----------------- fail -----------------')
        for k, i in fail.items():
            print(k)
            print(i[0])
            if i[1]:
                print(i[1])
            print("exit code:", i[2])
        raise er.CmdExecutionError(cmd)
    return 0
