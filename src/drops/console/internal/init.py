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


def new_init(arg):
    objPath = os.path.join(drops.__path__[0], 'docker_ops')
    pwd = os.getcwd()
    for i in os.listdir(objPath):
        p = os.path.join(objPath, i)
        t = os.path.join(pwd, i)
        if os.path.isdir(p):
            shutil.copytree(p, t)
        else:
            shutil.copyfile(p, t)


def add_init_cmd(s):
    p = s.add_parser(
        'init', help='Initialize the drops project in the current path.')
    p.set_defaults(func=new_init)
