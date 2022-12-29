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


def new_cmd(arg):
    from . import config
    from . import internal

    if arg.name in os.listdir(os.getcwd()):
        internal.Fatal("File exists: ", os.path.join(os.getcwd(), arg.name))
        return
    objPath = drops.__path__[0]
    shutil.copytree(os.path.join(objPath, 'docker_ops'),
                    os.path.join(os.getcwd(), arg.name))
    os.chdir(arg.name)
    c = config.Conf().open()
    c.setProjectName(arg.name)
    c.save()


def add_new_cmd(s):
    p = s.add_parser(
        'new', help='Create a drops project.')
    p.add_argument("name", metavar="name",
                   type=str, help="项目名。")
    p.set_defaults(func=new_cmd)
