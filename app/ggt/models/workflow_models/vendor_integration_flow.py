from cachetools import cached, LRUCache, TTLCache

from ggt.lib.utils import (
    x_response
)

from ggt.models.process_models.bp_vendor_integration import (
    bp_lab_status_update,
)

########################################################################################################
# [Public] functions
########################################################################################################

def lab_status_update(lab_status_update_request):
    return x_response(
        bp_lab_status_update(lab_status_update_request)
    )
########################################################################################################
# [Protected] functions
########################################################################################################
