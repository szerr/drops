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

from .cmd import *
from .globa import *
from . import cmd
import sys

def initCmd(p, s):
    # 在全局参数中汇总远程信息，接下来生成本次执行的环境配置。
    p.add_argument('-H', '--host',
        help="Connect to host via ssh. By default, execute in the current local directory.", default='', nargs='?', type=str)
    p.add_argument('-p', '--port',
        help="SSH port, default 22.", default=22, nargs='?', type=int)
    p.add_argument('-u', '--username',
        help="User for login, default root.", default='root', nargs='?', type=str)
    p.add_argument('-i', '--identity-file',
        help='Identity file. default: "./secret/id_*" or "~/.ssh/id_*".', default='', nargs='?', type=str)
    p.add_argument('-P', '--password',
        help="Login password. identity file is recommended for authentication.", default='', nargs='?', type=str)
    p.add_argument('-e', '--env',
        help="Specify the deployment environment. Configured in drops.yaml. execute locally by default. ", default='', nargs='?', type=str)
    p.add_argument('-E', '--encoding',
        help="The encoding of the remote server, default utf-8.", default='utf-8', nargs='?', type=str)
    p.add_argument('-d', '--deploy-path',
        help="The deployment path on the remote server. Local deployment does not work. defaut /srv/drops", default='/srv/drops', nargs='?', type=str)
    p.add_argument('-c', '--config',
        help="Specify an alternate config file. default: drops.yaml.", default='drops.yaml', nargs='?', type=str)
    
    # 初始化各个命令和参数
    for i in dir(cmd):
        if i.startswith('add_') and i.endswith('_cmd'):
            getattr(cmd, i)(s)

    # 非 debug 模式禁用
    if '--debug' in sys.argv:
        add_clean_up_cmd(s)
        add_undeploy_cmd(s)

def initHost():
    pass