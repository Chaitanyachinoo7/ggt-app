# system
import uvicorn
# third party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ggt.lib.constants import (
    DESCRIPTION,
    NOT_FOUND,
    CLINICAL_PROVIDER_RT_TAG,
    PATIENT_RT_TAG,
    BACKGROUND_TASK_RT_TAG,
    ADMIN_PORTAL_RT_TAG,
    CONTACT_CENTER_RT_TAG,
    PRINTER_HUB_RT_TAG,
    CARE_PROVIDER_RT_TAG,
    BILLER_APP_TAG
)

from ggt.lib.utils import (
    get_config_val,
    init_cloud_logger
)
# local
from ggt.routers import (
    rt_redirect,
    rt_clinical_provider,
    rt_patient,
    rt_task,
    rt_portal,
    rt_contact_center,
    rt_printer_hub,
    rt_care_provider,
    rt_billing
)

init_cloud_logger()

docs_url = None if (get_config_val('env') == 'PROD') else '/docs'
redoc_url = None if (get_config_val('env') == 'PROD') else '/redoc'

app = FastAPI(docs_url=docs_url, redoc_url=redoc_url)


origins = [
    "https://gogettested.com",
    "https://schedule.gogettested.com",
    "https://start.gogettested.com",
    "https://start-dev.gogettested.com",
    "https://start-qa.gogettested.com",
    "https://portal.gogettested.com",
    "https://portal-dev.gogettested.com",
    "https://portal-qa.gogettested.com",
    "https://ops.gogettested.com",
    "https://ops-dev.gogettested.com",
    "https://ops-qa.gogettested.com",
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

app.include_router(
    rt_redirect.router,
    tags=["Page Redirects"],
)

############################################################
# rt_clinical_provider route is only for role - Clinical Provider   #
############################################################
app.include_router(
    rt_clinical_provider.router,
    prefix="/api/provider",
    tags=[CLINICAL_PROVIDER_RT_TAG],
    responses={404: {DESCRIPTION: NOT_FOUND}},
)

############################################################
# rt_care_provider route is only for role - Clinical Provider   #
############################################################
app.include_router(
    rt_care_provider.router,
    prefix="/api/care_provider",
    tags=[CARE_PROVIDER_RT_TAG],
    responses={404: {"description": NOT_FOUND}},
)

############################################################
# rt_billing route is only for role - Clinical Provider   #
############################################################
app.include_router(
    rt_billing.router,
    prefix="/api/billing",
    tags=[BILLER_APP_TAG],
    responses={404: {"description": NOT_FOUND}},
)

############################################################
# rt_patient route is Open                                 #
############################################################
app.include_router(
    rt_patient.router,
    prefix="/api",
    tags=[PATIENT_RT_TAG],
    responses={404: {DESCRIPTION: NOT_FOUND}},
)

############################################################
# rt_task route is only for role - Super Admin             #
############################################################
app.include_router(
    rt_task.router,
    prefix="/api/task",
    tags=[BACKGROUND_TASK_RT_TAG],
    responses={404: {DESCRIPTION: NOT_FOUND}},
)

############################################################
# rt_portal route is only for role - Site Admin            #
############################################################
app.include_router(
    rt_portal.router,
    prefix="/api/portal",
    tags=[ADMIN_PORTAL_RT_TAG],
    responses={404: {DESCRIPTION: NOT_FOUND}},
)

#############################################################
# rt_contact_center route is only for role - Contact Center #
#############################################################
app.include_router(
    rt_contact_center.router,
    prefix="/api/cc",
    tags=[CONTACT_CENTER_RT_TAG],
    responses={404: {DESCRIPTION: NOT_FOUND}},
)

#############################################################
# rt_printer_hub Machine to Machine call                    #
#############################################################
app.include_router(
    rt_printer_hub.router,
    prefix="/api/print",
    tags=[PRINTER_HUB_RT_TAG],
    responses={404: {DESCRIPTION: NOT_FOUND}},
)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8888)
    #uvicorn.run(app, host='0.0.0.0', port=8000)
