import os

import modal
from fastapi import FastAPI
from pydantic import BaseModel


def _modal_app_name():
    return os.getenv("MODAL_APP_NAME") or "ggt-compute"


def _modal_secret_name():
    return os.getenv("MODAL_SECRET_NAME") or "ggt-env"


app = modal.App(_modal_app_name())

image = (
    modal.Image.debian_slim(python_version="3.8")
    .pip_install_from_requirements("requirements.txt")
)

secret = modal.Secret.from_name(_modal_secret_name())


@app.function(image=image, secrets=[secret], timeout=60)
def ping():
    return {"status": "ok"}


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def process_email_queue(batch_size: int = 10000, offset: int = 0):
    from ggt.tasks.email_queue_processor import task_process_email_queue

    return task_process_email_queue(batch_size, offset)


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def process_sms_queue(batch_size: int = 10000, offset: int = 0):
    from ggt.tasks.sms_queue_processor import task_process_sms_queue

    return task_process_sms_queue(batch_size, offset)


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def process_inbound_lab_reports():
    from ggt.tasks.lab_integration.inbound.process_inbound_orders import (
        task_process_inbound_results,
    )

    return task_process_inbound_results()


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def process_outbound_lab_orders():
    from ggt.tasks.lab_integration.outbound.process_outbound_orders import (
        task_process_outbound_orders,
    )

    return task_process_outbound_orders()


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def process_hl7_lab_orders():
    from ggt.tasks.hl7_outbound_lab_orders import task_process_hl7_lab_orders

    return task_process_hl7_lab_orders()


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def process_crl_lab_orders():
    from ggt.tasks.CRL_outbound_lab_orders import task_process_crl_lab_orders

    return task_process_crl_lab_orders()


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def generate_schedule(location_id: str):
    from ggt.models.workflow_models.clinical_test_site_admin_flow import (
        generate_schedule as _generate_schedule,
    )

    return _generate_schedule(location_id)


@app.function(image=image, secrets=[secret], timeout=60 * 60)
def generate_all_schedules():
    from ggt.models.workflow_models.clinical_test_site_admin_flow import (
        generate_all_schedules as _generate_all_schedules,
    )

    return _generate_all_schedules()


class _EmailQueueRequest(BaseModel):
    batch_size: int = 10000
    offset: int = 0


class _SmsQueueRequest(BaseModel):
    batch_size: int = 10000
    offset: int = 0


class _GenerateScheduleRequest(BaseModel):
    location_id: str


@app.function(image=image, secrets=[secret])
@modal.asgi_app()
def api():
    api_app = FastAPI()

    @api_app.get("/health")
    async def health():
        return ping()

    @api_app.post("/tasks/process_email_queue")
    async def api_process_email_queue(payload: _EmailQueueRequest):
        return process_email_queue(payload.batch_size, payload.offset)

    @api_app.post("/tasks/process_sms_queue")
    async def api_process_sms_queue(payload: _SmsQueueRequest):
        return process_sms_queue(payload.batch_size, payload.offset)

    @api_app.post("/tasks/process_inbound_lab_reports")
    async def api_process_inbound_lab_reports():
        return process_inbound_lab_reports()

    @api_app.post("/tasks/process_outbound_lab_orders")
    async def api_process_outbound_lab_orders():
        return process_outbound_lab_orders()

    @api_app.post("/tasks/process_hl7_lab_orders")
    async def api_process_hl7_lab_orders():
        return process_hl7_lab_orders()

    @api_app.post("/tasks/process_crl_lab_orders")
    async def api_process_crl_lab_orders():
        return process_crl_lab_orders()

    @api_app.post("/tasks/generate_schedule")
    async def api_generate_schedule(payload: _GenerateScheduleRequest):
        return generate_schedule(payload.location_id)

    @api_app.post("/tasks/generate_all_schedules")
    async def api_generate_all_schedules():
        return generate_all_schedules()

    return api_app

