from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.workflow_models.reporting_flow import get_stats_today, get_stats_by_date, get_sms_stats_by_date, \
    get_email_stats_by_date, aging_samples_with_lab, get_user_activity, get_patient_drill_down_by_date, \
    get_portal_stats_today
from ggt.models.data_models.data_types import PermissionsEnum as p, SummaryByDate, UserActivity, PatientDrilldownRequest

router = APIRouter()


@router.post("/get_stats_today", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_stats_today():
    return get_stats_today()


@router.get("/get_portal_stats_today")
async def api_get_portal_stats_today(user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return get_portal_stats_today(user)


@router.post("/get_stats_by_date")
async def api_get_stats_by_date(summary_by_bate: SummaryByDate, user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return get_stats_by_date(summary_by_bate.date, user)


@router.post("/get_sms_stats_by_date", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_sms_stats_by_date(summary_by_bate: SummaryByDate):
    return get_sms_stats_by_date(summary_by_bate.date)


@router.post("/get_email_stats_by_date", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_email_stats_by_date(summary_by_bate: SummaryByDate):
    return get_email_stats_by_date(summary_by_bate.date)


@router.get("/aging_samples_with_lab", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_aging_samples_with_lab():
    return aging_samples_with_lab()


@router.post("/user_activity", dependencies=[Security(authorize_user, scopes=[p.CREATE_LOCATION])])
async def api_user_activity(req: UserActivity):
    return get_user_activity(req)


@router.post("/get_patient_drill_down_by_date")
async def api_patient_drill_down_by_date(patient_drill_down_request: PatientDrilldownRequest,
                                         user=Security(authorize_user, scopes=[p.CREATE_LOCATION])):
    return get_patient_drill_down_by_date(user, patient_drill_down_request)
