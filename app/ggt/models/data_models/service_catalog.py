from typing import List, Set, Dict, Tuple, Optional
from datetime import date
from ggt.lib.utils import (
    get_config_val,
    log_generic,
    whoami
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.lib.adapters.mysql_adapter import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    exec_batch_execute
)

from ggt.models.data_models.data_types import (
    GgtServiceCatalogItem
    # GgtScheduleSlot,
    # GgtDateTimeLocation
)


########################################################################################################
# [Public] functions
########################################################################################################
def get_all_services():
    try:
        sql = "SELECT * FROM services_catalog"
        return read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


########################################################################################################
# [Protected] functions
########################################################################################################
