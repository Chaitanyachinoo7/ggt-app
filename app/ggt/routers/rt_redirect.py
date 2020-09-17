from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get("/")
async def ggt_home():
    return RedirectResponse(url="https://gogettested.com")
