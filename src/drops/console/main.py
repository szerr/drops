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

desc = '''drops 是基于 ssh 和 docker-compose 的运维模板，附带的 drops 命令可以方便的管理项目，部署服务。'''


def main():
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('--debug',
                        help="启动 debug 模式。", default=False, action='store_true')
    # metavar 设置空字符串，为了不以  {cmd1, cmd2, ..} 的形式显示可用子命令。
    subparsers = parser.add_subparsers(metavar="")
    # 初始化命令行参数
    pkg.init_argument(parser, subparsers)
    # 解析参数
    args = parser.parse_args()
    if args.version:
        # 输出版本号
        from .pkg import version
        print(version.__version__)
        return 0
    pkg.globa.args = args
    # 调用相关命令，没有命令时打印 help
    if 'func' in args:
        if not args.debug:
            try:
                status = args.func(args)
                return status
            except Exception as e:
                pkg.globa.thread_exit = True
                print('Fatal:', type(e).__name__, ':', e)
                return 126
        else:
            pkg.biz.log.set_level(pkg.biz.log.DEBUG)
            return args.func(args)
    else:
        parser.print_help()
    return 0


if __name__ == "__main__":
    import pkg  # 为了单个文件调试
    sys.exit(main())
else:
    from . import pkg  # 同时又能作为包被引入
