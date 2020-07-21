from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request
)

from ggt.tasks.inbound_lab_reports import task_process_inbound_lab_reports
from ggt.tasks.outbound_lab_orders import task_process_outbound_lab_orders
from ggt.tasks.report_notifications import task_schedule_result_notifications_and_followups
from ggt.tasks.email_queue_processor import task_process_email_queue
from ggt.tasks.sms_queue_processor import task_process_sms_queue
from ggt.tasks.call_queue_processor import task_process_voice_queue

router = APIRouter()

#TODO: With Cloud Run, consider Disabling Background Task. Ideally all asynchronous operations finish before delivering response
@router.post("/process_inbound_lab_reports")
async def api_process_inbound_lab_reports(request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_inbound_lab_reports)
    return {"status": "success"}


@router.post("/process_process_outbound_lab_orders")
async def api_process_outbound_lab_orders(request: Request):
    task_process_outbound_lab_orders()
    return {"status": "success"}


@router.post("/schedule_result_notifications_and_followups")
async def api_schedule_result_notifications_and_followups(request: Request):
    task_schedule_result_notifications_and_followups()
    return {"status": "success"}


@router.post("/process_email_queue")
async def api_process_email_queue(request: Request):
    task_process_email_queue()
    return {"status": "success"}


@router.post("/process_sms_queue")
async def api_process_sms_queue(request: Request):
    task_process_sms_queue()
    return {"status": "success"}


@router.post("/process_voice_queue")
async def api_process_voice_queue(request: Request):
    task_process_voice_queue()
    return {"status": "success"}
