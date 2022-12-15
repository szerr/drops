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

# 是否打印异常跟踪
DEBUG = False


def main():
    parser = argparse.ArgumentParser(description=desc)
    # metavar 设置空字符串，为了不以  {cmd1, cmd2, ..} 的形式显示可用子命令，怪怪的。
    subparsers = parser.add_subparsers(metavar="")

    internal.initCmd(subparsers)

    arg = parser.parse_args()
    # 调用相关命令，没有命令时打印 help
    if 'func' in arg:
        if not DEBUG:
            try:
                arg.func(arg)
            except Exception as e:
                print("Fatal:", e)
                sys.exit(1)
        else:
            arg.func(arg)
    else:
        parser.print_help()


if __name__ == "__main__":
    import internal  # 为了单个文件调试
    main()
else:
    from . import internal  # 同时又能作为包被引入
