from aiocache import cached

from ggt.lib.utils import (
    log_generic,
    x_response,
    y_response,
    whoami
)

from ggt.models.process_models.bp_portal_experience import (
    bp_cc_view_test_details,
    bp_cc_search_details_by_name_and_dob,
)
from ggt.models.process_models.bp_contact_center import(
    bp_cc_update_outbound_call_status
)

import ggt.lib.constants as c


########################################################################################################
# [Public] functions
########################################################################################################

async def cc_view_test_details(auth_token, test_id):
    return x_response(
        await bp_cc_view_test_details(
            test_id
        )
    )


async def cc_search_details_by_name_and_dob(last_name, dob):
    return y_response(
        await bp_cc_search_details_by_name_and_dob(
            last_name, dob
        )
    )


async def cc_update_outbound_call_status(test_id,
                                         first_name,
                                         test_date,
                                         dob,
                                         token,
                                         to_email,
                                         to_number,
                                         test_result,
                                         call_status):
    await bp_cc_update_outbound_call_status(
        test_id,
        first_name,
        test_date,
        dob,
        token,
        to_email,
        to_number,
        test_result,
        call_status
    )
########################################################################################################
# [Protected] functions
########################################################################################################
