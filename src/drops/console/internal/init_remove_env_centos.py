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


def add_init_env_centos_cmd(s):
    p = s.add_parser(
        'init_env_centos', help='初始化 centos 系远程环境，请自备 docker 源。')
    internal.add_arg_group_host(p)
    p.set_defaults(func=init_env_centos_cmd)


def init_env_centos_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    bin = 'yum install -y rsync docker-compose'
    internal.exec(bin, hosts)
