#system

#third party
from fastapi import FastAPI, Request, Response, Depends, Header, BackgroundTasks, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse

#local
from ggt.routers import users, items


app = FastAPI()
templates = Jinja2Templates(directory="templates")

origins = [
    "https://gogettested.com",
    "https://schedule.gogettested.com",
    "https://start.gogettested.com",
    "https://start-dev.gogettested.com",
    "https://start-qa.gogettested.com",
    "http://localhost",
    "http://localhost:5000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def ggt_home(request: Request):
    return RedirectResponse(url="https://gogettested.com")

'''
async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


app.include_router(users.router)
app.include_router(
    items.router,
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)
'''