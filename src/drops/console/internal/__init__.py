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

from .cmd import *
from .globals import *

def initCmd(p, s):
    # 在全局参数中汇总远程信息，接下来生成本次执行的环境配置。
    p.add_argument('-H', '--host',
        help="Connect to host via ssh. By default, execute in the current local directory.", default=False, action='store_true')
    p.add_argument('-p', '--port',
        help="SSH port, default 22.", default='22', action='store_true')
    p.add_argument('-u', '--username',
        help="User for login, default root.", default='root', action='store_true')
    p.add_argument('-i', '--identity-file',
        help='Identity file. default: "./secrets/id_*" or "~/.ssh/id_*".', default=False, action='store_true')
    p.add_argument('-P', '--password',
        help="Login password. identity file is recommended for authentication.", default=False, action='store_true')
    p.add_argument('-e', '--env',
        help="Specify the deployment environment. Configured in drops.yaml.", default='drops.yaml', action='store_true')
    p.add_argument('-E', '--encoding',
        help="The encoding of the remote server, default utf-8.", default='utf-8', action='store_true')
    p.add_argument('-d', '--deploy-path',
        help="The deployment path on the remote server. Local deployment does not work.", default=False, action='store_true')
    p.add_argument('-c', '--config',
        help="Specify an alternate config file. default: drops.yaml.", default='drops.yaml', action='store_true')
    
    # 初始化各个命令和参数
    add_new_cmd(s)
    add_ps_cmd(s)
    add_init_cmd(s)
    add_host_cmd(s)
    add_sync_cmd(s)
    add_deploy_cmd(s)
    add_redeploy_cmd(s)
    add_init_env_debian_cmd(s)
    add_nginx_reload_cmd(s)
    add_nginx_force_reload_cmd(s)
    add_stop_cmd(s)
    add_rm_cmd(s)
    add_kill_cmd(s)
    add_up_cmd(s)
    add_start_cmd(s)
    add_restart_cmd(s)
    add_project_cmd(s)
    add_echo_paths_cmd(s)
    add_pull_cmd(s)
    add_deploy_https_cert_cmd(s)
    add_logs_cmd(s)
    add_exec_cmd(s)
    add_backup_cmd(s)

def initHost():
    pass