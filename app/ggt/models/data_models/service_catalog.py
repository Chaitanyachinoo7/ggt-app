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

from ggt.lib.db import (
    exec_insert,
    exec_update,
    exec_delete,
    read_row,
    read_rows,
    replica_read_row,
    replica_read_rows
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
        sql = """SELECT 
                   *
                FROM
                    services_catalog;"""
        return replica_read_rows(sql)

    except Exception as err:
        log_generic(
            type=ERROR,
            function=whoami(),
            error=err
        )
        return None


def get_all_services_patient():
    try:
        sql = """SELECT 
                    sc.id AS service_id,
                    sc.service_code,
                    sc.service_name,
                    sp.*
                FROM
                    services_catalog sc
                        JOIN
    services_payments sp ON sc.id = sp.service_catalog_id;"""
        return replica_read_rows(sql)

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
