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

from . import globa, er


def join_path(*p):
    # 用 `/` 字符连接路径
    p_li = []
    for i in p:
        p_li.append('/'.join([i for i in os.path.split(i) if i]))
    return '/'.join(p_li)


def work_path():
    # 当前 drops 项目绝对路径，drops.yaml 所在目录
    return os.getcwd()


def deploy_path(env):
    return env.get_deploy_path()


def volumes_path(env):
    # volumes路径
    return join_path(deploy_path(env), 'volumes')
