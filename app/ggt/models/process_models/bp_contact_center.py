from ggt.models.data_models.contact_center import(
    update_outbound_call_status
)


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
    update_outbound_call_status(test_id,
                                first_name,
                                test_date,
                                dob,
                                token,
                                to_email,
                                to_number,
                                test_result,
                                call_status)
