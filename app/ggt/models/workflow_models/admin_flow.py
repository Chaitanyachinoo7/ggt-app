from aiocache import cached

from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_get_all_test_results,
    bp_get_general_search_results
)


########################################################################################################
# [Public] functions
########################################################################################################


async def admin_get_all_test_results():
    return y_response(
        awaitbp_get_all_test_results()
    )


async def admin_generic_search(search_arr):
    return y_response(
        await bp_get_general_search_results(search_arr)
    )

########################################################################################################
# [Protected] functions
########################################################################################################
