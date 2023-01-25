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
from . import er


def add_backup_cmd(s):
    p = s.add_parser(
        'backup', help='基于 rsync --del --link-dest 的增量备份。更改参数前先测试，以免写错删掉已有的备份文件。')
    internal.add_arg_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=backup_cmd)
    p.add_argument('obj', type=str, default='volumes', choices=[
        'docker',  'release', 'servers', 'var', 'volumes', 'ops', 'all'], nargs='?',
        help='''同步的文件夹。docker: docker-compose，ops 是除 var 和 volumes 的所有。''')
    p.add_argument('-t', '--target',
                   help="目标路径", default='backup/')
    p.add_argument('-d', '--time-format', default='%Y-%m-%d_%H:%M:%S',
                   help='目标路径下创建文件夹名的时间模板，与 python time.strftime format 参数相同。如 %%Y-%%m-%%d_%%H:%%M:%%S')
    p.add_argument('-l', '--link-dest',
                   help='未更改时链接到指定文件夹。默认是备份路径中符合 format 排序后最大的文件夹。')
    p.add_argument('-k', '--keep',
                   type=int, help="保留的备份个数，只有 format 开启时启用。本次备份也算一个。-1 保留所有。", default='-1')
    p.add_argument("-c", '--cod',
                   help="在目标路径创建项目名命名的文件夹", default=False, action='store_true')


def backup_cmd(p):
    host = internal.get_arg_host_from_conf(p)
    if not os.path.isdir(p.target):
        os.mkdir(p.target)
    return internal.backup(host,  p.obj, p.target, p.time_format, p.link_dest, p.keep, p.cod, p.force)
