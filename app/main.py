# system

# third party
from fastapi import FastAPI, Request, Response, Depends, Header, BackgroundTasks, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

# local
from ggt.routers import (
    rt_redirect, 
    rt_provider, 
    rt_patient, 
    rt_task, 
    rt_portal,
    rt_contact_center,
    rt_printer_hub
)

from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    FAILED,
    INFO,
    ERROR,
    NOT_FOUND
)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#Disable pubishing API documentation
#app.redoc_url = None
#app.docs_url = None


origins = [
    "https://gogettested.com",
    "https://schedule.gogettested.com",
    "https://start.gogettested.com",
    "https://start-dev.gogettested.com",
    "https://start-qa.gogettested.com",
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5000",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/private/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


app.include_router(
    rt_redirect.router,
    tags=["Page Redirects"],
)


app.include_router(
    rt_provider.router,
    prefix="/api/provider",
    tags=["Clinical Provider App"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": NOT_FOUND}},
)


app.include_router(
    rt_patient.router,
    prefix="/api",
    tags=["Patient Front End"],
    responses={404: {"description": NOT_FOUND}},
)


app.include_router(
    rt_task.router,
    prefix="/api/task",
    tags=["Background Tasks"],
    responses={404: {"description": NOT_FOUND}},
)

app.include_router(
    rt_portal.router,
    prefix="/api/portal",
    tags=["Admin Portal"],
    responses={404: {"description": NOT_FOUND}},
)

app.include_router(
    rt_contact_center.router,
    prefix="/api/cc",
    tags=["Contact Center App"],
    #dependencies=[Depends(get_token_header)],
    responses={404: {"description": NOT_FOUND}},
)

app.include_router(
    rt_printer_hub.router,
    prefix="/api/print",
    tags=["Printer Hub"],
    responses={404: {"description": NOT_FOUND}},
)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5000)
    #uvicorn.run(app, host='0.0.0.0', port=8000)