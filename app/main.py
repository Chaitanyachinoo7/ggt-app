# system
import uvicorn

# third party
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# local
import ggt.lib.constants as c
from ggt.lib.utils import (
    get_config_val as cfg,
    app_init
)
import sys, os
from ggt.routers import (
    rt_redirect,
    rt_clinical_provider,
    rt_patient,
    rt_task,
    rt_portal,
    rt_contact_center,
    rt_printer_hub,
    rt_care_provider,
    rt_billing,
    rt_reporting, 
    rt_management,
    rt_vendor
)

app_init()
app = FastAPI(
    docs_url=cfg('docs.swagger_url'),
    redoc_url=cfg('docs.redoc_url')
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg('origins'),
    allow_origin_regex='https?://.*',
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=512
)

app.include_router(
    rt_redirect.router,
    tags=[c.PAGE_REDIRECTS_RT_TAG],
)

############################################################
# rt_clinical_provider route is only for role - Clinical Provider   #
############################################################
app.include_router(
    rt_clinical_provider.router,
    prefix=c.CLINICAL_PROVIDER_PATH_PREFIX,
    tags=[c.CLINICAL_PROVIDER_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

############################################################
# rt_care_provider route is only for role - Clinical Provider   #
############################################################
app.include_router(
    rt_care_provider.router,
    prefix=c.CARE_PROVIDER_PATH_PREFIX,
    tags=[c.CARE_PROVIDER_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

############################################################
# rt_billing route is only for role - Clinical Provider   #
############################################################
app.include_router(
    rt_billing.router,
    prefix=c.BILLING_PATH_PREFIX,
    tags=[c.BILLING_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

############################################################
# rt_patient route is Open                                 #
############################################################
app.include_router(
    rt_patient.router,
    prefix=c.PATIENT_PATH_PREFIX,
    tags=[c.PATIENT_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

############################################################
# rt_task route is only for role - Super Admin             #
############################################################
app.include_router(
    rt_task.router,
    prefix=c.BACKGROUND_TASK_PATH_PREFIX,
    tags=[c.BACKGROUND_TASK_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

############################################################
# rt_portal route is only for role - Site Admin            #
############################################################
app.include_router(
    rt_portal.router,
    prefix=c.ADMIN_PORTAL_PATH_PREFIX,
    tags=[c.ADMIN_PORTAL_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

#############################################################
# rt_contact_center route is only for role - Contact Center #
#############################################################
app.include_router(
    rt_contact_center.router,
    prefix=c.CONTACT_CENTER_PATH_PREFIX,
    tags=[c.CONTACT_CENTER_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

#############################################################
# rt_printer_hub Machine to Machine call                    #
#############################################################
app.include_router(
    rt_printer_hub.router,
    prefix=c.PRINTER_HUB_PATH_PREFIX,
    tags=[c.PRINTER_HUB_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

#############################################################
# rt_reporting                                              #
#############################################################
app.include_router(
    rt_reporting.router,
    prefix=c.REPORTING_PATH_PREFIX,
    tags=[c.REPORT_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)


#############################################################
# rt_management                                             #
#############################################################
app.include_router(
    rt_management.router,
    prefix=c.MANAGEMENT_PATH_PREFIX,
    tags=[c.MANAGEMENT_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

############################################################
# rt_vendor route is only for role - Vendors or API Key   #
############################################################
app.include_router(
    rt_vendor.router,
    prefix=c.VENDOR_PATH_PREFIX,
    tags=[c.VENDOR_RT_TAG],
    responses={404: {c.DESCRIPTION: c.NOT_FOUND}},
)

#############################################################
# To Run Locally                                             #
#############################################################
if __name__ == '__main__':
    uvicorn.run(
        app,
        host=cfg('server.host'),
        port=cfg('server.port'),
        debug=cfg('log_level')
    )
