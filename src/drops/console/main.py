#!/bin/env python3

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

import argparse
import sys

from . import internal

desc = '''drops 是基于 ssh 和 docker-compose 的运维模板，附带的 drops 命令可以方便的管理项目，部署服务。'''

# 是否打印异常跟踪


def main():
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--debug',
                        help="启动 debug 模式。", default=False, action='store_true')
    subparsers = parser.add_subparsers()
    # 初始化命令行参数
    internal.initCmd(parser, subparsers)
    # 解析参数
    args = parser.parse_args()

    # python3 main.py -H example.com -p 1 -u r -i ~/.ssh/id_ed25519 -P 1 -e production -E utf-8 -d /srv/drops -c drops.yaml
    # print('host', args.host)
    # print('port', args.port)
    # print('username', args.username)
    # print('identity_file', args.identity_file)
    # print('password', args.password)
    # print('env', args.env)
    # print('encoding', args.encoding)
    # print('deploy_path', args.deploy_path)
    # print('config', args.config)

    internal.globa.args = args

    # 调用相关命令，没有命令时打印 help
    if 'func' in args:
        if not args.debug:
            try:
                args.func(args)
            except Exception as e:
                print('Fatal:', type(e).__name__, ':', e)
                sys.exit(1)
        else:
            internal.globa.debug_model = True
            args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    import internal  # 为了单个文件调试
    main()
else:
    from . import internal  # 同时又能作为包被引入

