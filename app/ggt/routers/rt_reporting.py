from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.workflow_models.reporting_flow import get_stats_today, get_stats_by_date, get_sms_stats_by_date, \
    get_email_stats_by_date
from ggt.models.data_models.data_types import PermissionsEnum as p, SummaryByDate

router = APIRouter()


@router.post("/get_stats_today", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_stats_today():
    return await get_stats_today()


@router.post("/get_stats_by_date", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_stats_by_date(summary_by_bate: SummaryByDate):
    return await get_stats_by_date(summary_by_bate.date)


@router.post("/get_sms_stats_by_date", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_sms_stats_by_date(summary_by_bate: SummaryByDate):
    return await get_sms_stats_by_date(summary_by_bate.date)


@router.post("/get_email_stats_by_date", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_email_stats_by_date(summary_by_bate: SummaryByDate):
    return await get_email_stats_by_date(summary_by_bate.date)
