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

import drops
from .config import Conf


def add_init_cmd(s):
    p = s.add_parser(
        'init', help='在当前目录初始化项目。')
    p.set_defaults(func=new_init)
    p.add_argument("projectName", metavar="projectName",
                   type=str, help="项目名。", nargs='?')


def new_init(p):
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    pwd = os.getcwd()
    if p.projectName == None:
        p.projectName = os.path.split(pwd)[-1]

    for i in os.listdir(objPath):
        s = os.path.join(objPath, i)
        t = os.path.join(pwd, i)
        if os.path.isdir(s):
            shutil.copytree(s, t)
        else:
            shutil.copyfile(s, t)

    c = Conf()
    c.setProjectName(p.projectName)
