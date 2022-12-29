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


def add_nginx_force_reload_cmd(s):
    p = s.add_parser(
        'nginxForceReload', help="重载 nginx 配置，会重载证书。")
    internal.add_arg_group_host(p)
    p.set_defaults(func=nginx_force_reload_cmd)


def nginx_force_reload_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    internal.exec(internal.docker_cmd_template(
        "exec -d nginx nginx -g 'daemon on; master_process on;' -s reload"), hosts)
