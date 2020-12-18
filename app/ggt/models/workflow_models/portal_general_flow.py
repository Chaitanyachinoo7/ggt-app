from cachetools import cached, LRUCache, TTLCache

from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_user_role
)

########################################################################################################
# [Public] functions
########################################################################################################


@cached(cache=TTLCache(maxsize=1024, ttl=300))
def portal_get_user_role(email):
    return bp_get_user_role(email)

########################################################################################################
# [Protected] functions
########################################################################################################
