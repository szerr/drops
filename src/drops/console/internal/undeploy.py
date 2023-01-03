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


def add_undeploy_cmd(s):
    p = s.add_parser(
        'undeploy', help='清理掉服务器上的容器和项目')
    internal.add_arg_group_host(p)
    internal.add_arg_force(p)
    p.set_defaults(func=undeploy_cmd)


def undeploy_cmd(p):
    if not p.force and not internal.user_confirm('即将进行反部署，这会清理掉服务器上的容器及 '+internal.container_path()+' 目录，但不会完全删除映射文件。是否继续？'):
        raise er.UserCancel
    hosts = internal.get_arg_group_host_from_conf(p)
    print('---------- kill ----------')
    internal.docker_compose_cmd('kill', hosts)
    print('--------- rm -f ---------')
    internal.docker_compose_cmd('rm -f', hosts)
    print('-------- rm -rf %s --------' % internal.container_path())
    internal.exec('rm -rf %s' % internal.container_path(), hosts)
