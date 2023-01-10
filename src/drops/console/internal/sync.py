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
from . import internal


def add_sync_cmd(s):
    p = s.add_parser(
        'sync', help='rsync 当前项目到远程服务器')
    internal.add_arg_group_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=sync_cmd)
    p.add_argument('obj', type=str, choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'all'], nargs='?',
        help='''同步的对象。docker: docker-compose，all 是除 var 和 volumes 的所有。默认：all
var, volumes 建议只用来同步初始数据。
同步 var, volumes 会检查远程目录是否为空文件夹，并做相应提示。''')


def sync_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    return internal.rsync(hosts, p.force, p.obj)
