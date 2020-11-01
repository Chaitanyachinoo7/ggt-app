from fastapi import APIRouter, Security
from fastapi.responses import RedirectResponse

from ggt.lib.auth import authorise_user
from ggt.models.data_models.data_types import (
    PermissionsEnum as p
)

router = APIRouter()


@router.get("/", dependencies=[Security(authorise_user, scopes=[p.ANONYMOUS])])
async def ggt_home():
    return RedirectResponse(url="https://gogettested.com")
