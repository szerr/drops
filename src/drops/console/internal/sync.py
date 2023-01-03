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
        'ops', 'volumes', 'all'], nargs='?', help="同步的对象。volumes 特指 volumes 目录，ops 是除 volumes 外其他所有，all 同步所有。default all。")


def sync_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    return internal.rsync(hosts, p.force)
