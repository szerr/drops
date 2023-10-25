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
    from . import globa
except:
    import drops.console.pkg.globa as globa

# self.args 是类接收到的所有参数。这样写只是为了少些两行代码，忽视可维护和语法检查。


class DropsErr(Exception):
    pass


class ThisIsNotDropsProject(DropsErr):
    def __str__(self):
        cwd = os.path.split(os.getcwd())[-1]
        return '"%s" is not a drops project, drops.yaml does not exist.' % cwd


class NoProjectNameOrDeploymentSet(DropsErr):
    def __str__(self):
        return 'No project name or deployment path set.'


class ProjectNameCannotBeEmpty(DropsErr):
    def __str__(self):
        return 'Project name cannot be empty.'


class RemotePathIsNotDropsProject(DropsErr):
    def __str__(self):
        return 'Remote host "%s" is not a drops project, docker-compose.yaml does not exist.' % self.args[0]


class FileOrFolderDoesNotExist(DropsErr):
    def __str__(self):
        return 'File or folder does not exist.' + self.args[0]


class UserCancel(DropsErr):
    def __str__(self):
        return "用户取消。"


class ConfigFileAlreadyExists(DropsErr):
    def __str__(self):
        return '%s already exists.' % globa.config_file


class FileOrDirAlreadyExists(DropsErr):
    def __str__(self):
        return 'File or directory already exists: ' + ''.join(self.args)


class PwdAndKeyCannotBeEmpty(DropsErr):
    def __str__(self):
        return 'Password and key cannot be empty at the same time.'


class ArgsError(DropsErr):
    def __str__(self):
        return 'Args error: %s.' % (' '.join(self.args))


class UnsupportedSyncObject(DropsErr):
    def __str__(self) -> str:
        return 'Unsupported sync object: %s.' % (' '.join(self.args))


class UnsupportedBackupObject(DropsErr):
    def __str__(self) -> str:
        return 'Unsupported backup object: %s.' % (' '.join(self.args))


class CmdNotExist(DropsErr):
    def __str__(self) -> str:
        return '[%s] command does not exist, please install it manually.' % (', '.join(self.args))


class HostExisted(DropsErr):
    def __str__(self):
        return 'Host existed: %s.' % self.args[0]


class ConfigurationFileFormatError(DropsErr):
    def __str__(self):
        return 'Configuration file format error: %s' % self.args[0]


class ConfigurationFileMissObj(DropsErr):
    def __str__(self):
        return 'The configuration file is missing %s.' % self.args[0]


class EnvDoesNotExist(DropsErr):
    def __str__(self):
        return 'Host %s does not exist' % self.args[0]


class CmdCannotContain(DropsErr):
    def __str__(self):
        return 'Command cannot contain "%s".' % self.args[0]


class CmdExecutionError(DropsErr):
    def __str__(self):
        return 'Command execution error: "%s".' % self.args[0]

# 不能同时设置 env 和 host


class EnvHostSimult(DropsErr):
    def __str__(self):
        return 'Cannot set env(-e) and host(-H) simultaneously.'


class EnvParameterRequired(DropsErr):
    def __str__(self) -> str:
        return 'The env(-e, --env) parameter is required.'


class NoDefaultEnvironmentIsSet(DropsErr):
    def __str__(self) -> str:
        return 'No default environment is set.'


class NoDropsDirProject(DropsErr):
    def __str__(self) -> str:
        return 'No drops dir in the "%s".' % self.args[0]


class NoSupportedScriptFound(DropsErr):
    def __str__(self) -> str:
        return 'No supported script found.'
