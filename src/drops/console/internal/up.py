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


def add_up_cmd(s):
    p = s.add_parser(
        'up', help='创建和启动容器。')
    internal.add_arg_group_host(p)
    internal.add_arg_service(p)
    p.set_defaults(func=up_cmd)


def up_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    b = 'up -d '
    if p.service:
        b += ' ' + p.service
    return internal.docker_compose_cmd(b, hosts)
