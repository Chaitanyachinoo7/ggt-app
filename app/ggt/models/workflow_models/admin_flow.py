from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_all_test_results
)


########################################################################################################
# [Public] functions
########################################################################################################

def admin_get_all_test_results():
    return y_response(
        bp_get_all_test_results()
    )



########################################################################################################
# [Protected] functions
########################################################################################################
