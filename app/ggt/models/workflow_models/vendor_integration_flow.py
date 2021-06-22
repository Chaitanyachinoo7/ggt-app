from cachetools import cached, LRUCache, TTLCache

from ggt.lib.utils import (
    x_response
)

from ggt.models.process_models.bp_vendor_integration import (
    bp_lab_status_update,
    bp_get_vaccine_status
)

########################################################################################################
# [Public] functions
########################################################################################################

def lab_status_update(lab_status_update_request):
    return x_response(
        bp_lab_status_update(lab_status_update_request)
    )

def get_vaccine_status(query):
    return x_response(
        bp_get_vaccine_status(query)
    )
########################################################################################################
# [Protected] functions
########################################################################################################
