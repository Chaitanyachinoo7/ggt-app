from fastapi import APIRouter, Request

from ggt.models.data_models.data_types import (
    CcLoginRequest, 
    CcPatientSearchRequest,
    CcTestLookupRequest
)

from ggt.models.workflow_models.contact_center_flows import (
    cc_login,
    cc_patient_search,
    cc_view_test_details
)

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
