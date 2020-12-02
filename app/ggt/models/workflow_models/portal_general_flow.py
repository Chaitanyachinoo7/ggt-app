from aiocache import cached

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


@cached(ttl=60)
def portal_get_user_role(email):
    return bp_get_user_role(email)

########################################################################################################
# [Protected] functions
########################################################################################################
