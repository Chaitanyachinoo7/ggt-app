from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

import ggt.lib.constants as c

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows
)

########################################################################################################
# [Public] functions
########################################################################################################

#def get_audience():