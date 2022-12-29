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

# 避免出现 "ImportError: attempted relative import with no known parent package"。
try:
    from . import globals
except:
    import globals

# self.args 是类接收到的所有参数。这样写只是为了少些两行代码，忽视可维护和语法检查。


class DropsErr(Exception):
    pass


class ThisIsNotDropsProject(DropsErr):
    def __str__(self):
        cwd = os.path.split(os.getcwd())[-1]
        return '"%s" is not a drops project, drops.yaml does not exist.' % cwd


class RemotePathIsNotDropsProject(DropsErr):
    def __str__(self):
        return 'Remote host "%s" is not a drops project, docker-compose.yaml does not exist.' % self.args[0]


class UserCancel(DropsErr):
    def __str__(self):
        return "用户取消。"


class ConfigFileAlreadyExists(DropsErr):
    def __str__(self):
        return '%s already exists.' % globals.confFileName


class PwdAndKeyCannotBeEmpty(DropsErr):
    def __str__(self):
        return 'Password and key cannot be empty at the same time.'


class ArgsError(DropsErr):
    def __str__(self):
        return 'Args error: %s.' % (' '.join(self.args))


class RsyncNotExist(DropsErr):
    def __str__(self) -> str:
        return 'rsync command does not exist, please install it manually.'


class HostExisted(DropsErr):
    def __str__(self):
        return 'Host existed: %s.' % self.args[0]


class ConfigurationFileFormatError(DropsErr):
    def __str__(self):
        return 'Configuration file format error.'


class HostGroupNotExist(DropsErr):
    def __str__(self):
        return 'Host group "%s" does not exit.' % self.args[0]


class HostNotInGroup(DropsErr):
    def __str__(self):
        return 'Host "%s" is not in group "%s".' % (self.args[1], self.args[0])


class CmdCannotContain(DropsErr):
    def __str__(self):
        return 'Command cannot contain "%s".' % self.args[0]


class CmdExecutionError(DropsErr):
    def __str__(self):
        return 'Command execution error: "%s".' % self.args[0]
