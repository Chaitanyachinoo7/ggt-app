from fastapi import APIRouter, Request

from ggt.models.data_models.data_types import (
    CcLoginRequest,
    CcPatientSearchRequest,
    CcTestLookupRequest
)

from ggt.models.workflow_models.contact_center_flows import (
    cc_login,
    cc_patient_search,
    cc_view_test_details,
    cc_patient_lookup
)
from ggt.lib.sms import(send_sms)

router = APIRouter()


@router.post("/login")
async def api_cc_login(cc_login_request: CcLoginRequest):
    return cc_login(
        cc_login_request.token)


@router.post("/patient_search")
async def api_cc_patient_search(cc_patient_search_request: CcPatientSearchRequest):
    return cc_patient_search(
        cc_patient_search_request.auth_token,
        cc_patient_search_request.last_name,
        cc_patient_search_request.dob)


@router.post("/view_test_details")
async def api_cc_view_test_details(cc_test_lookup_request: CcTestLookupRequest):
    return cc_view_test_details(
        cc_test_lookup_request.auth_token,
        cc_test_lookup_request.test_id
    )


@router.get("/patient_lookup")
async def api_cc_patient_lookup(request: Request):
    print(request)
    return cc_patient_lookup(
        request.headers['fname'], request.headers['lname'], request.headers['dob']
    )


@router.get("/sendsms")
async def api_cc_send_sms(request: Request):
    try:
        print(request)
        search_result = cc_patient_lookup(
            request.headers['fname'], request.headers['lname'], request.headers['dob']
        )
        print(search_result)
        if search_result['status'] == "success" and search_result['results'][0]['test_result'] == "neg":
            send_sms("+14372309014", "Hi There")
            return {"status": "success"}
        else:
            return {"status": "failure"}
    except Exception as err:
        print(err)
