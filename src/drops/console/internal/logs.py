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


from . import internal


def add_logs_cmd(s):
    p = s.add_parser(
        'logs', help='输出容器日志。')
    p.add_argument("container", metavar="container",
                   type=str, help="容器名")
    p.add_argument("-f", '--follow',
                   help="持续日志输出。", default=False, action='store_true')
    internal.add_arg_group_host(p)
    p.set_defaults(func=logs_cmd)


def logs_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    b = 'logs '
    if p.follow:
        b += '-f '
    return internal.docker_compose_cmd(b+p.container, hosts)
