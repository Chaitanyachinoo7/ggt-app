# system
import logging
import uuid
import uvicorn
from mangum import Mangum

# third party
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

# local
import ggt.lib.constants as c
from ggt.lib.utils import (
    get_config_val as cfg,
    # app_init
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
    rt_vendor,
    rt_payment,
)

logging.basicConfig(level=logging.INFO)

_env_val = str(cfg('env'))
_is_local_env = "LOCAL" in _env_val


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


# app_init()
app = FastAPI(
    title="GGT",
    description="GGT API",
    version="2.5.0",
    docs_url=cfg('docs.swagger_url'),
    redoc_url=cfg('docs.redoc_url')
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg('origins'),
    allow_origin_regex='https?://.*' if _is_local_env else None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=512
)

app.add_middleware(RequestIdMiddleware)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "")
    logging.exception("Unhandled exception", extra={"request_id": request_id})
    return JSONResponse(
        status_code=500,
        content={
            c.STATUS: c.FAILED,
            c.DESCRIPTION: "Internal Server Error",
            "request_id": request_id,
        },
    )


@app.on_event("startup")
async def validate_startup_config():
    required_keys = [
        "env",
        "server.host",
        "server.port",
        "origins",
        "docs.swagger_url",
        "docs.redoc_url",
    ]
    missing = []
    for k in required_keys:
        try:
            cfg(k)
        except Exception:
            missing.append(k)
    if missing:
        logging.error("Missing config keys: %s", ",".join(missing))
        if os.getenv("STRICT_CONFIG") == "1":
            raise RuntimeError("Missing config keys: {}".format(",".join(missing)))


@app.get("/healthz")
async def healthz():
    return {c.STATUS: c.SUCCESS}


@app.get("/readyz")
async def readyz():
    if os.getenv("READYZ_CHECK_DB") == "1":
        try:
            import mysql.connector

            cnx = mysql.connector.connect(
                user=cfg("databases.mysql.username"),
                password=cfg("databases.mysql.password"),
                host=cfg("databases.mysql.host"),
                database=cfg("databases.mysql.db"),
                use_pure=False,
                autocommit=True,
            )
            cur = cnx.cursor()
            cur.execute("SELECT 1")
            cur.fetchone()
            cur.close()
            cnx.close()
        except Exception:
            logging.exception("Readiness DB check failed")
            return JSONResponse(
                status_code=503,
                content={c.STATUS: c.FAILED, c.DESCRIPTION: "Not Ready"},
            )
    return {c.STATUS: c.SUCCESS}


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

############################################################
# rt_payment route is only payments                        #
############################################################

app.include_router(
    rt_payment.router,
    prefix=c.PAYMENT_CHECKOUT_PREFIX,
    tags=[c.PAYMENT_RT_TAG],
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


# Lambda function handler
handler = Mangum(app=app)
