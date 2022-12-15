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
        if a.host == None:
            raise er.ArgsError('the following arguments are required:', 'host')
        c = {'host': a.host, 'port': a.port,
             'username': a.username, 'coding': a.coding}
        if a.password is not None:
            c['password'] = a.password
        elif a.key is not None:
            c['key'] = a.key
        else:
            raise er.ArgsError('password and key must write one.')
        if a.cmd == 'change':
            config.Conf().change_host(group=a.group, **c)
        else:
            config.Conf().add_host(group=a.group, **c)

    elif a.cmd == 'drop':
        if a.host == None:
            raise er.ArgsError('the following arguments are required:', 'host')
        config.Conf().drop_host(group=a.group, host=a.host)
    elif a.cmd == 'ls':
        config.Conf().ls(group=a.group, host=a.host)
    else:
        raise er.ArgsError('cmd must be [ ls, add, drop, change ]')


def add_host_cmd(s):
    p = s.add_parser(
        'host', help='Manage drops hosts. password and key must write one.')
    p.add_argument("-g", '--group',
                   help="Add to host group (default to test host group).", type=str, default='test')
    p.add_argument('cmd', type=str, help="ls, add, drop, change")
    p.add_argument("host", metavar="ssh.example.com",
                   type=str, help="host.", default=None, nargs='?')
    p.add_argument("port", metavar="22",
                   type=int, help="ssh port.", default=22, nargs='?')
    p.add_argument("username", metavar="root",
                   type=str, help="ssh username.", default='root', nargs='?')
    p.add_argument('coding', metavar="coding",
                   type=str, help="shell coding, default is utf-8.", default='utf-8', nargs='?')
    p.add_argument("-p", '--password',
                   type=str, help="ssh password", default=None)
    p.add_argument("-k", '--key', metavar="~/.ssh/id_ed25519",
                   type=str, help="ssh key path", default=None)
    p.set_defaults(func=host_cmd)
