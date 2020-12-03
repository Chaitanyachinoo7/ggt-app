from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.data_models.data_types import (
    PermissionsEnum as p, GetBillingListReq, UpdateBilligStatus, InsuranceRecord, InsuranceUpdateRecord,
    InsuranceIDRecord)
from ggt.models.workflow_models.billing_flow import get_billing_list, update_billing_status, get_image_from_bucket, \
    get_report_from_bucket, create_insurance_record, update_insurance_record, validate_insurance_record, \
    delete_insurance_record, download_billing_list

router = APIRouter()


@router.post("/get_billing_list", dependencies=[Security(authorize_user, scopes=[p.GET_BILLING_LIST])])
async def api_get_billing_list(bill_req: GetBillingListReq):
    return await get_billing_list(bill_req)


@router.post("/update_billing_status", dependencies=[Security(authorize_user, scopes=[p.UPDATE_BILLING_STATUS])])
async def api_update_billing_status(bill_req: UpdateBilligStatus):
    return await update_billing_status(bill_req)


@router.get("/image/{image_id}", dependencies=[Security(authorize_user, scopes=[p.VIEW_INSURANCE_CARD])])
async def api_get_image_from_bucket(image_id: str):
    return await get_image_from_bucket(image_id)


@router.get("/report/{report_id}", dependencies=[Security(authorize_user, scopes=[p.VIEW_TEST_REPORT])])
async def api_get_report_from_bucket(report_id: str):
    return await get_report_from_bucket(report_id)


@router.post("/create_insurance_record", dependencies=[Security(authorize_user, scopes=[p.CREATE_INSURANCE_RECORD])])
async def api_create_insurance_record(record: InsuranceRecord):
    return await create_insurance_record(record)


@router.post("/update_insurance_record", dependencies=[Security(authorize_user, scopes=[p.UPDATE_INSURANCE_RECORD])])
async def api_update_insurance_record(record: InsuranceUpdateRecord):
    return await update_insurance_record(record)


@router.post("/validate_insurance_record", dependencies=[Security(authorize_user, scopes=[p.VALIDATE_INSURANCE_RECORD])])
async def api_validate_insurance_record(record: InsuranceIDRecord):
    return await validate_insurance_record(record)


@router.post("/delete_insurance_record", dependencies=[Security(authorize_user, scopes=[p.DELETE_INSURANCE_RECORD])])
async def api_delete_insurance_record(record: InsuranceIDRecord):
    return await delete_insurance_record(record)


@router.get("/download_billing_list/", dependencies=[Security(authorize_user, scopes=[p.GET_BILLING_LIST])])
async def api_download_billing_list(offset: int = 0, limit: int = 900):
    return await download_billing_list(offset, limit)


