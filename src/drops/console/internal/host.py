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


from . import er
from . import config


def host_cmd(a):
    if a.cmd == 'add' or a.cmd == 'change':
        if a.hostAlias == None:
            raise er.ArgsError('至少需要传入 hostAlias 参数')
        if a.host == None:
            raise er.ArgsError('至少需要传入 host 参数')
        c = {'host': a.host, 'port': a.port,
             'username': a.username, 'coding': a.coding, 'hostAlias': a.hostAlias}
        if a.password is not None:
            c['password'] = a.password
        elif a.key is not None:
            c['key'] = a.key
        else:
            raise er.ArgsError('密码或者 key 至少要传入一个。')
        if a.cmd == 'change':
            config.Conf().change_host(**c)
        else:
            config.Conf().add_host(**c)

    elif a.cmd == 'remove':
        if a.hostAlias == None:
            raise er.ArgsError('至少需要传入 hostAlias 参数')
        config.Conf().remove_host(a.hostAlias)
    elif a.cmd == 'ls':
        config.Conf().ls()
    else:
        config.Conf().ls()


def add_host_cmd(s):
    p = s.add_parser(
        'host', help='管理 drops 部署主机。因为密码是明文存储的，强烈建议用 key 做验证。')
    p.add_argument('cmd', type=str, choices=[
                   'ls', 'add', 'remove', 'change'], nargs='?', help="default ls")
    p.add_argument("hostAlias", metavar="default",
                   type=str, help="host 类型，比方说 default、test、dev、online。default 是关键字，所有命令不指定 --hostAlias 的话默认对 default 进行操作。")
    p.add_argument("host", metavar="ssh.example.com",
                   type=str, help="host.", default=None, nargs='?')
    p.add_argument("port", metavar="22",
                   type=int, help="ssh port.", default=22, nargs='?')
    p.add_argument("username", metavar="root",
                   type=str, help="ssh username.", default='root', nargs='?')
    p.add_argument('coding', metavar="coding",
                   type=str, help="shell coding, default is utf-8.", default='utf-8', nargs='?')
    p.add_argument("-p", '--password',
                   type=str, help="ssh password. Note that the password is stored in plain text, and key verification is strongly recommended.", default=None)
    p.add_argument("-k", '--key', metavar="~/.ssh/id_ed25519",
                   type=str, help="ssh key path", default=None)
    p.set_defaults(func=host_cmd)
