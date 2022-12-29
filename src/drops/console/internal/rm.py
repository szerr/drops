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
from . import er


def add_rm_cmd(s):
    p = s.add_parser(
        'rm', help='删除容器。')
    internal.add_arg_group_host(p)
    internal.add_arg_service(p)
    internal.add_arg_force(p)
    p.set_defaults(func=rm_cmd)


def rm_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    b = 'rm -f'
    if p.service:
        if not p.force and not internal.user_confirm('确认删除 ', p.service, '？'):
            raise er.UserCancel
        b += ' ' + p.service
    if not p.force and not internal.user_confirm('确认删除所有容器？'):
        raise er.UserCancel
    return internal.docker_compose_cmd(b, hosts)
