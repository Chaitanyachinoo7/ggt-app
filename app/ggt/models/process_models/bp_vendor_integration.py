from datetime import datetime

import ggt.lib.constants as c
from ggt.lib.utils import (
    log_generic,
    whoami)

from ggt.models.data_models.lab import (
    lab_status_update
)


########################################################################################################
# [Public] functions
########################################################################################################

def bp_lab_status_update(lab_status_update_request):
    try:
        return lab_status_update(lab_status_update_request)

    except Exception as err:
        log_generic(
            type=c.ERROR,
            function=whoami(),
            error=err
        )
