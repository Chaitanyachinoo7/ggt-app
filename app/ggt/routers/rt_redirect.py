from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR
)

router = APIRouter()


@router.get("/")
async def ggt_home():
    return RedirectResponse(url="https://gogettested.com")
