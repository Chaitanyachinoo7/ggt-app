from starlette.responses import StreamingResponse

from ggt.lib.utils import (
    x_response,
    y_response
)
from ggt.models.process_models.bp_biller_experience import bp_get_billing_list, bp_update_billing_status, \
    bp_image_from_bucket, bp_report_from_bucket

from ggt.models.process_models.bp_care_provider_experience import (
    bp_get_provider_processing_list, bp_lock_provider_task, bp_create_patient_test_consultation,
    bp_update_consultation_note, bp_provider_complete_task, bp_provider_rollback_to_pending_task)


########################################################################################################
# [Public] functions
########################################################################################################

def get_billing_list(billing_request):
    return y_response(
        bp_get_billing_list(billing_request.offset, billing_request.status, billing_request.from_dt, billing_request.to_dt)
    )


def update_billing_status(billing_request):
    return x_response(
        bp_update_billing_status(billing_request.appointment_id)
    )


def get_image_from_bucket(image_id):
    return StreamingResponse(
        bp_image_from_bucket(image_id),
        media_type="image/png",
        headers={
            'Content-Disposition': 'inline; filename="insurance_card.png"'
        }
    )


def get_report_from_bucket(report_id):
    return StreamingResponse(
        bp_report_from_bucket(report_id),
        media_type="application/pdf",
        headers={
            'Content-Disposition': 'filename="report.pdf"'
        }
    )

########################################################################################################
# [Protected] functions
########################################################################################################
