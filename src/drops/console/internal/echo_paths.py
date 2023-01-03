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


def add_echo_paths_cmd(s):
    p = s.add_parser(
        'echoPaths', help='显示 drops 用到的各部署路径')
    p.set_defaults(func=deploy_echo_paths_cmd)


def deploy_echo_paths_cmd(p):
    print('容器路径，docker-compose.yaml 所在文件夹:', internal.container_path())
    print('发布路径，应用程序文件夹:', internal.release_path())
    print('volumes 路径，应用程序数据文件夹:', internal.volumes_path())
