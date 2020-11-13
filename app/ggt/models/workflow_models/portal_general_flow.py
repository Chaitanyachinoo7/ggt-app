from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_user_role
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

from ggt.lib.cache import (
    timed_lru_cache
)
########################################################################################################
# [Public] functions
########################################################################################################
@timed_lru_cache(seconds=60)
def portal_get_user_role(email):
    return bp_get_user_role(email)

########################################################################################################
# [Protected] functions
########################################################################################################
