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
from . import internal

import drops
from . import er


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
