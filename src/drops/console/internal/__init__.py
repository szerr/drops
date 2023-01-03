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

from .clean_up import *
from .undeploy import *

from .deploy import *
from .init_remove_env_debian import *
from .internal import *
from .new import *
from .nginx_force_reload import *
from .nginx_reload import *
from .ps import *
from .redeploy import *
from .sync import *
from .init import *
from .host import *
from .stop import *
from .rm import *
from .kill import *
from .up import *
from .start import *
from .restart import *
from .project import *
from .echo_paths import *
from .pull import *
from .deploy_https_key import *

def initCmd(s):
    add_clean_up_cmd(s)
    add_undeploy_cmd(s)

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
    add_deploy_https_key_cmd(s)
