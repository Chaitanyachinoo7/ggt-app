from fastapi import APIRouter, Security

from ggt.lib.auth import authorize_user
from ggt.models.workflow_models.reporting_flow import get_stats_today
from ggt.models.data_models.data_types import PermissionsEnum as p

router = APIRouter()


@router.post("/get_stats_today", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_get_stats_today():
    return await get_stats_today()
