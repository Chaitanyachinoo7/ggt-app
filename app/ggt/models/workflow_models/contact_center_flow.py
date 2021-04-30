from cachetools import cached, LRUCache, TTLCache

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
@cached(cache=TTLCache(maxsize=1024, ttl=120))
def cc_view_test_details(auth_token, test_id):
    return x_response(
        bp_cc_view_test_details(
            test_id
        )
    )


@cached(cache=TTLCache(maxsize=1024, ttl=60))
def cc_search_details_by_name_and_dob(last_name, dob):
    return y_response(
        bp_cc_search_details_by_name_and_dob(
            last_name, dob
        )
    )


def cc_update_outbound_call_status(test_id,
                                   first_name,
                                   test_date,
                                   dob,
                                   token,
                                   to_email,
                                   to_number,
                                   test_result,
                                   call_status):
    bp_cc_update_outbound_call_status(
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
