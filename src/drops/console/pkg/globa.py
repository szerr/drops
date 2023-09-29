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


# import logging
# log = logging.getLogger('drops')
# log.setLevel(logging.DEBUG)

# ch = logging.StreamHandler()
# formatter = logging.Formatter('%(levelname)s: %(message)s')
# ch.setFormatter(formatter)
# log.addHandler(ch)

# log.debug('debug message')
# log.info('info message')
# log.warning('warn message')
# log.error('error message')
# log.critical('critical message')

args = None

# 全局维护线程状态，需要退出时设置为 True
thread_exit = False
