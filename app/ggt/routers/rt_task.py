import ujson

import requests
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Request,
    Depends,
    HTTPException,
    Security
)

from ggt.lib.auth import authorize_user
from ggt.lib.constants import (
    STATUS,
    SUCCESS,
    DESCRIPTION,
    BACKGROUND_TASK_INITIATE_MESSAGE,
    AUTH_FAILED_MESSAGE
)
from ggt.tasks.archive_notifications import archive_processed_notifications
from ggt.tasks.generate_antigen_result_pdf import generate_antigen_results_pdf
from ggt.tasks.mass_sms_notifications import notify_patients
from ggt.tasks.outbound_external_lab_reports import list_ftp_files, \
    task_process_outbound_lab_reports, delete_ftp_files
from ggt.tasks.reminder_sms import (
    task_process_daily_sms_reminders,
    task_process_daily_email_reminders
)
from ggt.lib.utils import is_admin
from ggt.models.data_models.data_types import PermissionsEnum as p, PatientRelocateNotificationRequest, \
    PatientRescheduleNotificationRequest
from ggt.tasks.call_queue_processor import task_process_voice_queue
from ggt.tasks.email_queue_processor import task_process_email_queue
from ggt.tasks.inbound_lab_reports import task_process_inbound_lab_reports
from ggt.tasks.inbound_lab_reports import archive_stale_rpt_files
from ggt.tasks.locations_processor import task_populate_location_thumbnails
from ggt.tasks.locations_processor import task_populate_gps_coordinates
from ggt.tasks.misc_processor import task_process_misc
from ggt.tasks.appsheet_database_processor import rebuild_appsheet_database
# from ggt.tasks.outbound_lab_orders import task_process_outbound_lab_orders
from ggt.tasks.lab_integration.outbound.process_outbound_orders import task_process_outbound_orders
from ggt.tasks.lab_integration.inbound.process_inbound_orders import task_process_inbound_results

from ggt.tasks.hl7_outbound_lab_orders import task_process_hl7_lab_orders
from ggt.tasks.CRL_outbound_lab_orders import task_process_crl_lab_orders
from ggt.tasks.report_notifications import task_schedule_result_notifications_and_followups
from ggt.tasks.sms_queue_processor import task_process_sms_queue
from ggt.tasks.update_stripe_payments_processor import update_stripe_payments

router = APIRouter()


@router.post("/background_process_inbound_lab_reports", dependencies=[Security(authorize_user, scopes=[p.PROCESS_INBOUND_LAB_REPORTS])])
async def api_background_process_inbound_lab_reports(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_inbound_results)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/process_inbound_lab_reports", dependencies=[Security(authorize_user, scopes=[p.PROCESS_INBOUND_LAB_REPORTS])])
async def api_process_inbound_lab_reports():
    task_process_inbound_results()
    return {STATUS: SUCCESS}


@router.post("/background_process_outbound_lab_orders", dependencies=[Security(authorize_user, scopes=[p.PROCESS_PROCESS_OUTBOUND_LAB_ORDERS])])
async def api_background_process_outbound_lab_orders(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_outbound_orders)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/process_outbound_lab_orders", dependencies=[Security(authorize_user, scopes=[p.PROCESS_PROCESS_OUTBOUND_LAB_ORDERS])])
async def api_process_outbound_lab_orders():
    task_process_outbound_orders()
    return {STATUS: SUCCESS}


@router.post("/process_hl7_lab_orders", dependencies=[Security(authorize_user, scopes=[p.PROCESS_PROCESS_OUTBOUND_LAB_ORDERS])])
async def api_process_hl7_lab_orders(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_hl7_lab_orders)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/process_crl_lab_orders", dependencies=[Security(authorize_user, scopes=[p.PROCESS_PROCESS_OUTBOUND_LAB_ORDERS])])
async def api_process_crl_lab_orders(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_crl_lab_orders)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/archive_stale_rpt_files", dependencies=[Security(authorize_user, scopes=[p.PROCESS_PROCESS_OUTBOUND_LAB_ORDERS])])
async def api_archive_stale_rpt_files(background_tasks: BackgroundTasks):
    background_tasks.add_task(archive_stale_rpt_files)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/archive_processed_notifications", dependencies=[Security(authorize_user,  scopes=[p.ARCHIVE_PROCESSED_NOTIFICATIONS])])
async def api_archive_processed_notifications(background_tasks: BackgroundTasks):
    background_tasks.add_task(archive_processed_notifications)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/schedule_result_notifications_and_followups", dependencies=[Security(authorize_user, scopes=[p.SCHEDULE_RESULT_NOTIFICATIONS_AND_FOLLOWUPS])])
async def api_schedule_result_notifications_and_followups(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_schedule_result_notifications_and_followups)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/process_voice_queue", dependencies=[Security(authorize_user, scopes=[p.PROCESS_VOICE_QUEUE])])
async def api_process_voice_queue(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_voice_queue)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.get("/process_email_queue/{batch_size}/{offset}", dependencies=[Security(authorize_user, scopes=[p.PROCESS_EMAIL_QUEUE])])
async def api_process_email_queue(batch_size: int=10000, offset: int=0):
    task_process_email_queue(batch_size, offset)
    return {STATUS: SUCCESS}


@router.get("/process_sms_queue/{batch_size}/{offset}", dependencies=[Security(authorize_user, scopes=[p.PROCESS_SMS_QUEUE])])
async def api_process_sms_queue(batch_size: int=10000, offset: int=0):
    task_process_sms_queue(batch_size, offset)
    return {STATUS: SUCCESS}

'''
@router.get("/process_email_queue/{batch_size}/{offset}", dependencies=[Security(authorize_user, scopes=[p.PROCESS_EMAIL_QUEUE])])
async def api_process_email_queue(background_tasks: BackgroundTasks, batch_size: int = 10000, offset: int = 0):
    background_tasks.add_task(task_process_email_queue, batch_size, offset)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.get("/process_sms_queue/{batch_size}/{offset}", dependencies=[Security(authorize_user, scopes=[p.PROCESS_SMS_QUEUE])])
async def api_process_sms_queue(background_tasks: BackgroundTasks, batch_size: int = 10000, offset: int = 0):
    background_tasks.add_task(task_process_sms_queue, batch_size, offset)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }
'''


@router.post("/notify_patients_relocate", dependencies=[Security(authorize_user, scopes=[p.NOTIFY_PATIENTS])])
async def api_notify_patients(request: PatientRelocateNotificationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(notify_patients, request)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/notify_patients_reschedule", dependencies=[Security(authorize_user, scopes=[p.NOTIFY_PATIENTS])])
async def api_notify_patients(request: PatientRescheduleNotificationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(notify_patients, request)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/populate_location_thumbnails", dependencies=[Security(authorize_user, scopes=[p.POPULATE_LOCATION_THUMBNAILS])])
async def api_populate_location_thumbnails():
    task_populate_location_thumbnails()
    return {STATUS: SUCCESS}

# TODO: [GGT-127] create security permission


@router.post("/populate_gps_coordinates")
async def api_process_sms_queue(request: Request):
    task_populate_gps_coordinates()
    return {STATUS: SUCCESS}


@router.post("/misc_processor", dependencies=[Security(authorize_user, scopes=[p.MISC_PROCESSOR])])
async def api_misc_processor(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_misc)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/process_daily_appointment_reminders", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def reminder_sms():
    task_process_daily_sms_reminders()
    task_process_daily_email_reminders()
    return {STATUS: SUCCESS}


@router.get("/app_info_v2", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_app_info():
    r = requests.get('http://curlmyip.org/')
    return {
        'egress_ip': r.text,
        'version': '2020-12-23 05:06:00'
    }


@router.post("/export_external_outbound_reports", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_export_external_outbound_reports(background_tasks: BackgroundTasks):
    background_tasks.add_task(task_process_outbound_lab_reports)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/list_ftp_files", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_list_ftp_files():
    x = list_ftp_files()
    return {"response": x}


@router.post("/rebuild_appsheet_database", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_rebuild_appsheet_database(background_tasks: BackgroundTasks):
    background_tasks.add_task(rebuild_appsheet_database)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/process_appointments_against_stripe", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_process_appointments_against_stripe(background_tasks: BackgroundTasks):
    background_tasks.add_task(update_stripe_payments)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }


@router.post("/generate_antigen_results_pdf", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
async def api_generate_antigen_results_pdf(background_tasks: BackgroundTasks):
    background_tasks.add_task(generate_antigen_results_pdf)
    return {
        STATUS: SUCCESS,
        DESCRIPTION: BACKGROUND_TASK_INITIATE_MESSAGE
    }

# @router.post("/delete_ftp_files", dependencies=[Security(authorize_user, scopes=[p.ANONYMOUS])])
# async def api_delete_ftp_files():
#     x = delete_ftp_files()
#     return {"response": x}
