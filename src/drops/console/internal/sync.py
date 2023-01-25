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
