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

from . import globa
from . import log
import subprocess
import sys
import threading
import time


def join_path(*p):
    # 用 `/` 字符连接路径
    p_li = []
    for i in p:
        p_li.append('/'.join([i for i in os.path.split(i) if i]))
    return '/'.join(p_li)


class process():
    def __init__(self, command, intervals):
        self._intervals = intervals  # 重启间隔时间
        self._command_str = ' '.join(command)
        self._command = [
            i for i in self._command_str.split(' ') if i]  # 形成参数数组
        self._process = None
        self._event_li = []
        self._run_status = True
        self._t = threading.Thread(target=self.periodicRestart)
        self._t.start()

    def exit(self):
        self._run_status = False
        self.stop()

    def start(self):
        print("run>", self._command_str)
        self._process = subprocess.Popen(
            self._command, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)

    def stop(self):
        if self._process:
            print("kill>", self._command_str)
            self._process.kill()
            print("Wait for exit...")
            self._process.wait()

    def restart(self):
        self.stop()
        self.start()

    def add_event(self, e):
        self._event_li.append(e)

    def periodicRestart(self):
        # 每次保存可能会触发多个更改事件，增加计时器减少重启的次数。
        while self._run_status and not globa.thread_exit:
            time.sleep(self._intervals)
            if self._event_li:
                log.info("文件系统事件数量：", len(self._event_li))
                self._event_li = []
                self.restart()
