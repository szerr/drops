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


def add_deploy_https_key_cmd(s):
    p = s.add_parser(
        'deployHttpsKey', help='申请并部署 https 证书。')
    internal.add_arg_group_host(p)
    p.add_argument("-f", '--force',
                   help="重新申请证书。", default=False, action='store_true')
    p.set_defaults(func=deploy_https_key_cmd)


def deploy_https_key_cmd(p):
    hosts = internal.get_arg_group_host_from_conf(p)
    b = 'exec -T acme.sh redeploy-ssl'
    if p.force:
        b += ' --force'
    # redeploy-ssl 是作为文件映射进去的，需要重启才会更新。
    internal.docker_compose_cmd('restart acme.sh', hosts)
    print("开始申请证书，如果出现文件复制失败，请确认 nginx 容器是否正常运行。")
    return internal.docker_compose_cmd(b, hosts)
