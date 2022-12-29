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

from . import config


def add_project_cmd(s):
    p = s.add_parser(
        'project', help='项目信息')
    p.set_defaults(func=project_cmd)

    subparsers = p.add_subparsers(metavar="")
    n = subparsers.add_parser('name')
    n.add_argument('name', help="传入参数设置项目名，没有参数输出项目名",
                   type=str, nargs='?', default=None)


def project_cmd(p):
    c = config.Conf().open()
    if 'name' in p:
        if p.name == None:
            print(c.getProjectName())
        else:
            c.setProjectName(p.name)
    else:
        for k, i in c.C['project'].items():
            print(k, ': ', i, sep='')
