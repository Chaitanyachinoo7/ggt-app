from ggt.models.data_models.contact_center import(
    add_outbound_call_status,
    update_outbound_call_status
)
from datetime import datetime


def bp_cc_update_outbound_call_status(
    test_id,
    first_name,
    test_date,
    dob,
    token,
    to_email,
    to_number,
    test_result,
    call_status
):
    if call_status == "call_attempted":
        add_outbound_call_status(test_id,
                                 first_name,
                                 test_date,
                                 dob,
                                 token,
                                 to_email,
                                 to_number,
                                 test_result,
                                 call_status, datetime.now())
    else:
        update_outbound_call_status(test_id, call_status, call_status+"_dt", datetime.now())
